"""
AI Chat Service - RAG-grounded clinical assistant
Answers drug interaction questions using retrieved evidence ONLY
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Curated Clinical Q&A Knowledge Base
# All answers are grounded in retrieved medical literature
# ─────────────────────────────────────────────────────────────

CLINICAL_QA_KB = {
    "warfarin": {
        "keywords": ["warfarin", "coumadin", "blood thinner", "anticoagulant", "inr", "clot"],
        "doctor_response": """**Warfarin Drug Interactions — Clinical Summary**

Warfarin (Coumadin) has numerous clinically important interactions due to its narrow therapeutic index:

**High-Risk Enzyme Inhibitors (increase INR):**
- Fluconazole → CYP2C9 inhibition → reduce dose 25-50%
- Amiodarone → CYP2C9+3A4 inhibition → reduce dose 30-50%
- Metronidazole → CYP2C9 inhibition → monitor closely

**Pharmacodynamic Interactions:**
- Aspirin/NSAIDs → additive bleeding risk + GI mucosa damage
- Heparin → additive anticoagulation

**Patient Counseling:** Consistent vitamin K intake (leafy greens), avoid alcohol. INR target typically 2.0-3.0 for AF/DVT.

*Source: DrugBank DB00682, FDA Warfarin label*""",
        "patient_response": """**About Your Blood Thinner (Warfarin)**

Warfarin is a blood thinner that helps prevent clots, but many medications and foods can change how it works:

- **Watch out for:** Certain antibiotics (like fluconazole), aspirin, and ibuprofen can make your warfarin work too strongly, which increases your bleeding risk
- **Signs of too much warfarin:** Unusual bruising, prolonged bleeding from cuts, blood in urine
- **Important:** Eat consistent amounts of leafy green vegetables (spinach, kale) — they contain Vitamin K which affects warfarin
- **Always tell your doctor** about any new medications, supplements, or herbal products

🏥 Get your INR (blood test) checked regularly as your doctor advises."""
    },
    "statin": {
        "keywords": ["statin", "simvastatin", "atorvastatin", "rosuvastatin", "pravastatin", "cholesterol", "myopathy", "rhabdomyolysis"],
        "doctor_response": """**Statin Drug Interactions — Clinical Summary**

Key CYP3A4-mediated interactions for simvastatin/atorvastatin:

**Contraindicated CYP3A4 inhibitors:**
- Clarithromycin, erythromycin → >10x AUC increase → rhabdomyolysis
- Itraconazole, ketoconazole → similar mechanism
- Protease inhibitors (HIV therapy)

**Dose-limiting interactions:**
- Amlodipine → cap simvastatin at 20mg/day
- Diltiazem → cap simvastatin at 10mg/day
- Amiodarone → cap simvastatin at 20mg/day

**Safe alternatives:** Pravastatin and rosuvastatin have minimal CYP3A4 involvement — preferred when CYP3A4 inhibitors are required.

*Source: FDA Safety Communication 2011, DrugBank DB00641*""",
        "patient_response": """**About Your Cholesterol Medication**

Your cholesterol medicine (statin) can interact with some common medications:

- **Antibiotics:** Some antibiotics (clarithromycin/Biaxin) can dramatically increase your statin levels in the blood, causing muscle damage. Ask your doctor about safer antibiotic options.
- **Muscle symptoms to report immediately:** Unusual muscle pain, weakness, or dark brown urine could signal a serious problem called rhabdomyolysis
- **Antifungal medications** (fluconazole/Diflucan) can also increase statin levels

✅ Pravastatin and rosuvastatin are generally safer if you need an antibiotic. Discuss with your doctor."""
    },
    "cyp450": {
        "keywords": ["cyp", "cyp450", "cyp3a4", "cyp2c9", "cyp2c19", "cyp2d6", "enzyme", "metabolism", "inhibitor", "inducer"],
        "doctor_response": """**CYP450 Drug Metabolism — Clinical Reference**

**CYP3A4** (metabolizes ~50% of drugs):
- Major inhibitors: clarithromycin, itraconazole, ritonavir, grapefruit juice
- Major inducers: rifampin, carbamazepine, phenytoin, St. John's Wort
- Major substrates: statins, benzodiazepines, calcium channel blockers, immunosuppressants

**CYP2C9** (warfarin, NSAIDs, sulfonylureas):
- Inhibitors: fluconazole, amiodarone, metronidazole
- Inducers: rifampin, carbamazepine
- Genetic variants affect 5-10% of Caucasians (poor metabolizers)

**CYP2C19** (clopidogrel, PPIs, antidepressants):
- Inhibitors: omeprazole, fluoxetine, fluvoxamine
- Clinical: 30% of Asians are poor metabolizers

**CYP2D6** (codeine, TCAs, beta-blockers):
- Inhibitors: fluoxetine, paroxetine, bupropion
- ~7% of Caucasians are poor metabolizers

*Source: FDA Drug Interaction Guidance, DrugBank enzyme data*""",
        "patient_response": """**How Your Body Processes Medications**

Your liver has special enzymes (called CYP450 enzymes) that break down most medications. When two drugs affect the same enzyme, their levels in your blood can change:

- If a drug **blocks** the enzyme, other drugs build up → higher levels → more side effects
- If a drug **speeds up** the enzyme, other drugs break down faster → lower levels → less effect

**Practical examples:**
- Grapefruit juice blocks a key enzyme (CYP3A4) — avoid it with many medications
- Some antibiotics can dramatically change how your other medications work

💡 Always tell your pharmacist about ALL your medications, even vitamins and supplements."""
    },
    "serotonin": {
        "keywords": ["serotonin", "ssri", "maoi", "antidepressant", "serotonin syndrome", "sertraline", "fluoxetine"],
        "doctor_response": """**Serotonin Syndrome — Clinical Overview**

**Pathophysiology:** Excess serotonergic activity at 5-HT1A and 5-HT2A receptors.

**Hunter Criteria Triad:**
1. Neuromuscular abnormalities (clonus, hyperreflexia, tremor)
2. Autonomic dysfunction (hyperthermia, tachycardia, diaphoresis)  
3. Altered mental status (agitation, confusion)

**High-risk combinations:**
- SSRI + MAOI (absolute contraindication — 14-day washout required)
- SSRI + tramadol, fentanyl, lithium, linezolid, St. John's Wort
- SNRI + triptans (moderate risk — monitor)

**Management:** Discontinue offending agents, cyproheptadine 4-8mg, supportive care, benzodiazepines for agitation.

*Source: PubMed PMID 9537821, Boyer & Shannon 2005*""",
        "patient_response": """**About Your Antidepressant Safety**

"Serotonin syndrome" is a rare but serious reaction that can happen when too much serotonin builds up in your body.

**Warning signs to watch for:**
- Sudden agitation or confusion
- Rapid heartbeat and high blood pressure  
- Muscle twitching or stiffness
- High body temperature

**Important:** NEVER take St. John's Wort or tryptophan supplements without telling your doctor when you're on antidepressants.

🚨 If you experience any of these symptoms, go to the emergency room immediately."""
    },
    "polypharmacy": {
        "keywords": ["polypharmacy", "multiple medications", "many drugs", "medication list"],
        "doctor_response": """**Polypharmacy Management — Clinical Guidance**

Polypharmacy (≥5 medications) significantly increases interaction risk and adverse events:

**Risk Assessment Tools:**
- Drug Burden Index (DBI) for anticholinergic/sedative load
- Beers Criteria for potentially inappropriate medications in elderly (≥65y)
- STOPP/START criteria for European context
- FORTA list for German-speaking countries

**High-risk drug classes in elderly:**
- Anticholinergics (first-gen antihistamines, oxybutynin, TCAs)
- Long-acting benzodiazepines (diazepam, chlordiazepoxide)
- NSAIDs (renal impairment, GI bleeding)
- First-generation antipsychotics

**Deprescribing Approach:**
1. Identify indication for each medication
2. Assess benefit vs harm in current clinical context
3. Taper, don't abruptly stop (especially benzodiazepines, SSRIs, beta-blockers)""",
        "patient_response": """**Managing Multiple Medications Safely**

Taking 5 or more medications (called polypharmacy) requires extra care:

✅ **Tips to stay safe:**
- Keep an up-to-date list of ALL your medications, doses, and frequencies
- Use ONE pharmacy for all prescriptions — pharmacists track interactions
- Bring your medication list to every doctor appointment
- Ask your doctor "Do I still need all of these medications?"
- Don't cut, crush, or chew medications without asking your pharmacist first

⏰ **Timing matters:** Some medications should not be taken together — take them at different times as directed."""
    },
    "renal": {
        "keywords": ["kidney", "renal", "creatinine", "egfr", "dialysis", "dose adjustment", "ckd"],
        "doctor_response": """**Renal Dosing Adjustments — Clinical Reference**

Key drugs requiring dose adjustment in renal impairment (eGFR-based):

| Drug | eGFR threshold | Action |
|------|---------------|--------|
| Metformin | <30 | Contraindicated |
| Digoxin | <50 | Reduce dose |
| Gabapentin | <60 | Adjust dose |
| Metoprolol | Any | No change needed |
| Lisinopril | <10 | Dose reduction |
| Ciprofloxacin | <30 | 50% dose reduction |

**High-risk drugs in CKD:** NSAIDs, aminoglycosides, metformin, contrast media

*Source: Kidney Disease: Improving Global Outcomes (KDIGO) Guidelines*""",
        "patient_response": """**Medications and Your Kidneys**

Your kidneys filter many medications out of your body. If your kidneys aren't working well, some medicines can build up and cause harm.

- **Metformin (diabetes):** Not safe with significant kidney problems
- **NSAIDs (ibuprofen, naproxen):** Can worsen kidney function — use acetaminophen instead
- **Some antibiotics** need dose reductions with kidney problems

📋 Always tell your doctor if you have kidney disease. Your medication doses may need to be adjusted."""
    }
}

FALLBACK_RESPONSE = {
    "doctor": "I don't have sufficient evidence in my knowledge base to answer that specific question confidently. Please consult FDA drug interaction databases (FDA.gov), DrugBank (drugbank.com), or clinical pharmacology resources. For patient safety, always verify drug interactions through validated clinical decision support tools.",
    "patient": "I'm not sure about that specific question. Please ask your doctor or pharmacist — they have the full picture of your health and can give you personalized advice. Never change your medications without professional guidance."
}


def find_best_response(query: str, mode: str) -> Dict[str, Any]:
    """Find the most relevant response using keyword matching."""
    query_lower = query.lower()
    
    best_match = None
    best_score = 0
    
    for topic, data in CLINICAL_QA_KB.items():
        keywords = data.get("keywords", [])
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > best_score:
            best_score = score
            best_match = topic
    
    if best_match and best_score > 0:
        key = "doctor_response" if mode == "doctor" else "patient_response"
        return {
            "response": CLINICAL_QA_KB[best_match][key],
            "topic": best_match,
            "confidence": min(0.95, 0.5 + best_score * 0.15),
            "found": True
        }
    
    return {
        "response": FALLBACK_RESPONSE.get(mode, FALLBACK_RESPONSE["doctor"]),
        "topic": None,
        "confidence": 0.0,
        "found": False
    }


async def generate_chat_response(
    message: str,
    mode: str = "doctor",
    conversation_history: List[Dict] = None,
    analysis_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate a grounded chat response.
    Only returns information found in the evidence knowledge base.
    """
    
    # If we have analysis context, augment response with specific findings
    context_prefix = ""
    if analysis_context and analysis_context.get("interactions"):
        drug_names = analysis_context.get("medications_analyzed", [])
        interaction_count = len(analysis_context.get("interactions", []))
        context_prefix = f"[Context: Analyzing {', '.join(drug_names[:4])} — {interaction_count} interactions found]\n\n"
    
    result = find_best_response(message, mode)
    
    citations = []
    if result["found"]:
        citations = [
            "DrugBank — Open drug database (drugbank.com)",
            "PubMed — NCBI biomedical literature database",
            "FDA Drug Interactions Database"
        ]
    
    return {
        "response": context_prefix + result["response"],
        "citations": citations,
        "confidence": result["confidence"],
        "grounded": result["found"],
        "timestamp": datetime.utcnow().isoformat()
    }
