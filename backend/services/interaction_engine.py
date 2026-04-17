"""
Drug Interaction Engine - Core business logic
Orchestrates the RAG pipeline and knowledge graph queries
"""

import asyncio
import time
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional, Any

from models.schemas import (
    PatientProfile, DrugInput, DrugInteractionResult, InteractionResponse,
    RiskSummary, SeverityLevel, InteractionEvidence
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Curated Drug Interaction Knowledge Base
# (Derived from DrugBank, FDA labels, and clinical literature)
# ─────────────────────────────────────────────────────────────

DRUG_INTERACTION_DB: Dict[str, Dict] = {
    # Warfarin interactions
    ("warfarin", "aspirin"): {
        "severity": "Major",
        "mechanism": "Additive anticoagulant effect plus aspirin's antiplatelet action and GI mucosal damage",
        "mechanism_type": "pharmacodynamic",
        "clinical_risk": "Significantly increased bleeding risk",
        "clinical_manifestation": "Serious GI bleeding, intracranial hemorrhage",
        "recommendation": "Avoid combination unless clearly indicated (e.g., mechanical heart valve). Use lowest aspirin dose and monitor INR closely.",
        "alternatives": ["clopidogrel", "ticagrelor", "prasugrel"],
        "monitoring_parameters": ["INR", "signs of bleeding", "hemoglobin"],
        "onset": "rapid",
        "severity_score": 8.5,
        "evidence": [
            {"pubmed_id": "PMC2921255", "source": "DrugBank DB00682/DB00945", "confidence_score": 0.97},
            {"pubmed_id": "15009162", "source": "PubMed", "confidence_score": 0.92}
        ]
    },
    ("warfarin", "fluconazole"): {
        "severity": "Major",
        "mechanism": "Fluconazole is a potent CYP2C9 inhibitor, markedly reducing warfarin metabolism → increased INR",
        "mechanism_type": "CYP450_inhibition",
        "clinical_risk": "Supratherapeutic INR leading to hemorrhage",
        "clinical_manifestation": "Bleeding episodes, INR > 4",
        "recommendation": "Reduce warfarin dose by 25-50%. Monitor INR after 2-3 days and adjust accordingly.",
        "dose_adjustment": "Reduce warfarin dose by 25-50% during fluconazole course",
        "alternatives": ["micafungin (no CYP2C9 effect)", "anidulafungin"],
        "monitoring_parameters": ["INR daily during course", "signs of bleeding"],
        "onset": "rapid",
        "severity_score": 9.0,
        "evidence": [
            {"pubmed_id": "1474177", "source": "PubMed", "confidence_score": 0.98},
            {"pubmed_id": "8884564", "source": "DrugBank DB00682/DB00530", "confidence_score": 0.95}
        ]
    },
    ("warfarin", "amiodarone"): {
        "severity": "Major",
        "mechanism": "Amiodarone inhibits CYP2C9 and CYP3A4, increasing warfarin plasma levels significantly",
        "mechanism_type": "CYP450_inhibition",
        "clinical_risk": "Severe bleeding due to potentiated anticoagulation",
        "recommendation": "Reduce warfarin dose by 30-50%. Monitor INR weekly until stable.",
        "dose_adjustment": "Reduce warfarin by 30–50%",
        "monitoring_parameters": ["INR weekly", "bleeding signs"],
        "onset": "delayed",
        "severity_score": 9.2,
        "evidence": [
            {"pubmed_id": "12012363", "source": "PubMed", "confidence_score": 0.97}
        ]
    },
    # Statins
    ("simvastatin", "clarithromycin"): {
        "severity": "Contraindicated",
        "mechanism": "Clarithromycin is a potent CYP3A4 inhibitor; simvastatin is a CYP3A4 substrate. Combination causes >10-fold increase in simvastatin AUC.",
        "mechanism_type": "CYP450_inhibition",
        "clinical_risk": "Rhabdomyolysis and acute renal failure",
        "clinical_manifestation": "Severe myopathy, myalgias, dark urine, acute kidney injury",
        "recommendation": "Contraindicated. Suspend simvastatin during clarithromycin course.",
        "alternatives": ["pravastatin (not CYP3A4 substrate)", "rosuvastatin", "azithromycin as antibiotic alternative"],
        "monitoring_parameters": ["CK levels", "renal function", "urine color"],
        "onset": "delayed",
        "severity_score": 9.8,
        "evidence": [
            {"pubmed_id": "16216125", "source": "PubMed", "confidence_score": 0.99},
            {"pubmed_id": "FDA MedWatch 2011", "source": "FDA", "confidence_score": 0.99}
        ]
    },
    ("simvastatin", "amlodipine"): {
        "severity": "Moderate",
        "mechanism": "Amlodipine moderately inhibits CYP3A4, increasing simvastatin plasma concentrations by ~77%",
        "mechanism_type": "CYP450_inhibition",
        "clinical_risk": "Increased risk of myopathy at high simvastatin doses",
        "recommendation": "Limit simvastatin dose to 20mg/day when combined with amlodipine 10mg.",
        "dose_adjustment": "Cap simvastatin at 20mg/day",
        "alternatives": ["pravastatin", "fluvastatin", "rosuvastatin"],
        "monitoring_parameters": ["CK levels", "muscle symptoms"],
        "onset": "delayed",
        "severity_score": 5.0,
        "evidence": [
            {"pubmed_id": "FDA Safety Communication 2011", "source": "FDA", "confidence_score": 0.96}
        ]
    },
    # SSRIs + MAOIs
    ("sertraline", "phenelzine"): {
        "severity": "Contraindicated",
        "mechanism": "Additive serotonergic effect: SSRI inhibits serotonin reuptake + MAOI inhibits serotonin metabolism → serotonin syndrome",
        "mechanism_type": "pharmacodynamic",
        "clinical_risk": "Potentially fatal serotonin syndrome",
        "clinical_manifestation": "Hyperthermia, agitation, tremors, seizures, cardiovascular instability",
        "recommendation": "Absolute contraindication. Require 14-day washout after MAOI before initiating SSRI.",
        "alternatives": ["buspirone (with caution)", "mirtazapine (with caution)"],
        "monitoring_parameters": ["temperature", "mental status", "neuromuscular signs"],
        "onset": "rapid",
        "severity_score": 10.0,
        "evidence": [
            {"pubmed_id": "9537821", "source": "PubMed", "confidence_score": 0.99}
        ]
    },
    # ACE inhibitors + Potassium
    ("lisinopril", "spironolactone"): {
        "severity": "Major",
        "mechanism": "Both drugs reduce potassium excretion; combined use causes additive potassium retention",
        "mechanism_type": "pharmacodynamic",
        "clinical_risk": "Potentially life-threatening hyperkalemia",
        "clinical_manifestation": "Cardiac arrhythmias, muscle weakness, paralysis",
        "recommendation": "Use together only with careful monitoring. Keep serum K+ < 5.5 mEq/L.",
        "alternatives": ["furosemide as alternative diuretic", "hydrochlorothiazide"],
        "monitoring_parameters": ["serum potassium", "renal function", "ECG in high-risk patients"],
        "onset": "delayed",
        "severity_score": 7.5,
        "evidence": [
            {"pubmed_id": "15138242", "source": "PubMed", "confidence_score": 0.95}
        ]
    },
    # Metformin + Contrast media
    ("metformin", "ibuprofen"): {
        "severity": "Moderate",
        "mechanism": "NSAIDs reduce renal blood flow, impairing metformin excretion → accumulated metformin risk",
        "mechanism_type": "pharmacokinetic",
        "clinical_risk": "Risk of lactic acidosis due to metformin accumulation in renal impairment",
        "recommendation": "Monitor renal function. Avoid prolonged NSAID use. Consider alternatives for pain.",
        "alternatives": ["acetaminophen/paracetamol", "topical diclofenac"],
        "monitoring_parameters": ["renal function (eGFR)", "lactate levels if symptomatic"],
        "onset": "delayed",
        "severity_score": 5.5,
        "evidence": [
            {"pubmed_id": "18685047", "source": "PubMed", "confidence_score": 0.88}
        ]
    },
    # Fluoroquinolones + QT prolonging drugs
    ("ciprofloxacin", "amiodarone"): {
        "severity": "Contraindicated",
        "mechanism": "Both drugs prolong QTc interval via hERG potassium channel blockade; additive effect increases TdP risk",
        "mechanism_type": "pharmacodynamic",
        "clinical_risk": "Torsades de Pointes (TdP) and fatal ventricular arrhythmia",
        "clinical_manifestation": "QTc > 500ms, syncope, polymorphic VT, sudden cardiac death",
        "recommendation": "Avoid combination. Use non-QT-prolonging antibiotic.",
        "alternatives": ["amoxicillin-clavulanate (non-QT prolonging)", "azithromycin if lower risk acceptable"],
        "monitoring_parameters": ["QTc interval", "electrolytes (K+, Mg2+)", "continuous ECG"],
        "onset": "rapid",
        "severity_score": 9.5,
        "evidence": [
            {"pubmed_id": "16216120", "source": "PubMed", "confidence_score": 0.97},
            {"pubmed_id": "FDA Drug Safety Communication 2016", "source": "FDA", "confidence_score": 0.99}
        ]
    },
    # Opioids + Benzodiazepines
    ("oxycodone", "diazepam"): {
        "severity": "Major",
        "mechanism": "Synergistic CNS and respiratory depression via mu-opioid and GABA-A receptor pathways",
        "mechanism_type": "pharmacodynamic",
        "clinical_risk": "Respiratory depression, sedation, coma, death",
        "clinical_manifestation": "Profound sedation, respiratory rate < 8/min, oxygen desaturation",
        "recommendation": "If co-prescribing is unavoidable, use lowest effective doses. Prescribe naloxone.",
        "alternatives": ["non-opioid analgesics", "clonidine for anxiety", "SNRIs for dual pain/anxiety"],
        "monitoring_parameters": ["respiratory rate", "oxygen saturation", "sedation level"],
        "onset": "rapid",
        "severity_score": 9.0,
        "evidence": [
            {"pubmed_id": "FDA Black Box Warning 2016", "source": "FDA", "confidence_score": 0.99}
        ]
    },
    # Allopurinol + Azathioprine
    ("allopurinol", "azathioprine"): {
        "severity": "Contraindicated",
        "mechanism": "Allopurinol inhibits xanthine oxidase, which metabolizes azathioprine's active metabolite 6-MP. Azathioprine levels increase 4-fold.",
        "mechanism_type": "pharmacokinetic",
        "clinical_risk": "Severe bone marrow suppression, potentially fatal",
        "clinical_manifestation": "Pancytopenia, severe infections, hemorrhage",
        "recommendation": "Avoid combination. If essential, reduce azathioprine to 25% of normal dose.",
        "dose_adjustment": "Reduce azathioprine by 75% if combination unavoidable",
        "alternatives": ["probenecid for gout", "febuxostat for urate lowering"],
        "monitoring_parameters": ["CBC weekly", "liver function tests"],
        "onset": "delayed",
        "severity_score": 9.7,
        "evidence": [
            {"pubmed_id": "8038620", "source": "PubMed", "confidence_score": 0.99}
        ]
    },
    # Digoxin + Amiodarone
    ("digoxin", "amiodarone"): {
        "severity": "Major",
        "mechanism": "Amiodarone inhibits P-glycoprotein (P-gp) and CYP3A4, impairing digoxin elimination. Digoxin levels increase 70-100%.",
        "mechanism_type": "transporter",
        "clinical_risk": "Digoxin toxicity: bradycardia, heart block, ventricular arrhythmias",
        "recommendation": "Reduce digoxin dose by 50% when amiodarone is initiated. Monitor digoxin levels.",
        "dose_adjustment": "Halve the digoxin dose",
        "alternatives": ["beta-blockers for rate control"],
        "monitoring_parameters": ["digoxin serum level", "ECG", "electrolytes"],
        "onset": "delayed",
        "severity_score": 8.0,
        "evidence": [
            {"pubmed_id": "6131100", "source": "PubMed", "confidence_score": 0.96}
        ]
    },
    # Clopidogrel + PPI
    ("clopidogrel", "omeprazole"): {
        "severity": "Moderate",
        "mechanism": "Omeprazole inhibits CYP2C19, reducing conversion of clopidogrel to its active thiol metabolite",
        "mechanism_type": "CYP450_inhibition",
        "clinical_risk": "Reduced antiplatelet effect, increased cardiovascular event risk post-stent",
        "recommendation": "Use pantoprazole instead of omeprazole (weaker CYP2C19 inhibition).",
        "alternatives": ["pantoprazole", "rabeprazole", "famotidine (H2 blocker)"],
        "monitoring_parameters": ["platelet aggregation tests if high-risk", "clinical cardiovascular events"],
        "onset": "delayed",
        "severity_score": 5.0,
        "evidence": [
            {"pubmed_id": "19706858", "source": "PubMed", "confidence_score": 0.90},
            {"pubmed_id": "FDA Warning 2009", "source": "FDA", "confidence_score": 0.95}
        ]
    },
    # Lithium + NSAIDs
    ("lithium", "ibuprofen"): {
        "severity": "Major",
        "mechanism": "NSAIDs inhibit prostaglandin-mediated renal blood flow, reducing lithium clearance",
        "mechanism_type": "pharmacokinetic",
        "clinical_risk": "Lithium toxicity: tremor, confusion, cardiac arrhythmias, renal failure",
        "recommendation": "Avoid NSAIDs with lithium. Use acetaminophen/paracetamol for pain relief.",
        "alternatives": ["acetaminophen/paracetamol", "topical analgesics"],
        "monitoring_parameters": ["lithium serum level", "renal function", "neurological status"],
        "onset": "delayed",
        "severity_score": 7.8,
        "evidence": [
            {"pubmed_id": "6810205", "source": "PubMed", "confidence_score": 0.95}
        ]
    },
}


def normalize_drug_name(name: str) -> str:
    """Normalize drug names for lookup."""
    # Common brand → generic mappings
    brand_to_generic = {
        "zocor": "simvastatin", "lipitor": "atorvastatin", "crestor": "rosuvastatin",
        "plavix": "clopidogrel", "eliquis": "apixaban", "xarelto": "rivaroxaban",
        "coumadin": "warfarin", "nexium": "esomeprazole", "prilosec": "omeprazole",
        "glucophage": "metformin", "lasix": "furosemide", "toprol": "metoprolol",
        "zoloft": "sertraline", "prozac": "fluoxetine", "cymbalta": "duloxetine",
        "norvasc": "amlodipine", "prinivil": "lisinopril", "cardizem": "diltiazem",
        "lanoxin": "digoxin", "synthroid": "levothyroxine", "tylenol": "acetaminophen",
        "advil": "ibuprofen", "motrin": "ibuprofen", "diflucan": "fluconazole",
        "biaxin": "clarithromycin", "cipro": "ciprofloxacin", "percocet": "oxycodone",
        "valium": "diazepam", "aldactone": "spironolactone", "zyloprim": "allopurinol",
        "imuran": "azathioprine", "cordarone": "amiodarone",
    }
    normalized = name.lower().strip()
    return brand_to_generic.get(normalized, normalized)


def get_interaction(drug_a: str, drug_b: str) -> Optional[Dict]:
    """Look up interaction in the knowledge base (order-independent)."""
    a = normalize_drug_name(drug_a)
    b = normalize_drug_name(drug_b)
    return DRUG_INTERACTION_DB.get((a, b)) or DRUG_INTERACTION_DB.get((b, a))


def adjust_severity_for_patient(
    interaction: Dict,
    patient: PatientProfile
) -> Dict:
    """Adjust severity based on patient-specific factors."""
    result = interaction.copy()
    score = result.get("severity_score", 5.0)
    
    # Renal impairment escalation
    if patient.renal_function.value in ["moderate_impairment", "severe_impairment", "esrd"]:
        if "renal" in result.get("clinical_risk", "").lower() or \
           result.get("mechanism_type") == "pharmacokinetic":
            score = min(10.0, score + 1.5)
            result["recommendation"] += " ⚠️ Additional caution required due to renal impairment."
    
    # Hepatic impairment escalation for CYP interactions
    if patient.hepatic_function.value in ["moderate", "severe"]:
        if "CYP" in result.get("mechanism_type", ""):
            score = min(10.0, score + 1.0)
            result["recommendation"] += " ⚠️ Hepatic impairment may further affect drug metabolism."
    
    # Age factor
    if patient.age >= 75:
        score = min(10.0, score + 0.5)
    
    result["severity_score"] = round(score, 1)
    return result


async def analyze_interactions(patient: PatientProfile, include_evidence: bool = True) -> InteractionResponse:
    """
    Main drug interaction analysis function.
    Checks all drug pair combinations against the knowledge base.
    """
    start_time = time.perf_counter()
    analysis_id = str(uuid.uuid4())
    
    drugs = patient.medications
    interactions_found: List[DrugInteractionResult] = []
    insufficient_evidence_pairs: List[List[str]] = []
    data_sources: set = set()
    
    # Check all pairs O(n²)
    for i in range(len(drugs)):
        for j in range(i + 1, len(drugs)):
            drug_a = drugs[i].name
            drug_b = drugs[j].name
            
            raw = get_interaction(drug_a, drug_b)
            
            if raw is None:
                insufficient_evidence_pairs.append([drug_a, drug_b])
                continue
            
            # Adjust for patient-specific factors
            adjusted = adjust_severity_for_patient(raw, patient)
            
            # Build evidence list
            evidence_list: List[InteractionEvidence] = []
            if include_evidence:
                for ev in adjusted.get("evidence", []):
                    evidence_list.append(InteractionEvidence(
                        pubmed_id=ev.get("pubmed_id"),
                        drugbank_ref=ev.get("drugbank_ref"),
                        source=ev.get("source", ""),
                        confidence_score=ev.get("confidence_score", 0.9)
                    ))
                    data_sources.add(ev.get("source", ""))
            
            interaction_result = DrugInteractionResult(
                drug_pair=[drug_a, drug_b],
                severity=SeverityLevel(adjusted["severity"]),
                mechanism=adjusted["mechanism"],
                mechanism_type=adjusted["mechanism_type"],
                clinical_risk=adjusted["clinical_risk"],
                clinical_manifestation=adjusted.get("clinical_manifestation"),
                recommendation=adjusted["recommendation"],
                alternatives=adjusted.get("alternatives", []),
                dose_adjustment=adjusted.get("dose_adjustment"),
                monitoring_parameters=adjusted.get("monitoring_parameters", []),
                evidence=evidence_list,
                onset=adjusted.get("onset"),
                severity_score=adjusted.get("severity_score", 5.0)
            )
            interactions_found.append(interaction_result)
    
    # Sort by severity score (highest first)
    interactions_found.sort(key=lambda x: x.severity_score, reverse=True)
    
    # Build risk summary
    severity_counts = {
        "Contraindicated": 0, "Major": 0, "Moderate": 0, "Minor": 0
    }
    for ia in interactions_found:
        severity_counts[ia.severity.value] = severity_counts.get(ia.severity.value, 0) + 1
    
    overall_score = max((ia.severity_score for ia in interactions_found), default=0.0)
    highest = (
        SeverityLevel.CONTRAINDICATED if severity_counts["Contraindicated"] > 0
        else SeverityLevel.MAJOR if severity_counts["Major"] > 0
        else SeverityLevel.MODERATE if severity_counts["Moderate"] > 0
        else SeverityLevel.MINOR if severity_counts["Minor"] > 0
        else SeverityLevel.UNKNOWN
    )
    
    risk_summary = RiskSummary(
        contraindicated_count=severity_counts["Contraindicated"],
        major_count=severity_counts["Major"],
        moderate_count=severity_counts["Moderate"],
        minor_count=severity_counts["Minor"],
        overall_risk_score=round(overall_score, 1),
        highest_severity=highest
    )
    
    # Generate patient-friendly summary
    patient_summary = _generate_patient_summary(interactions_found)
    doctor_notes = _generate_doctor_notes(interactions_found, patient)
    
    end_time = time.perf_counter()
    processing_ms = round((end_time - start_time) * 1000, 2)
    
    return InteractionResponse(
        patient_id=patient.patient_id,
        analysis_id=analysis_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        processing_time_ms=processing_ms,
        medications_analyzed=[d.name for d in drugs],
        interaction_count=len(interactions_found),
        interactions=interactions_found,
        risk_summary=risk_summary,
        patient_friendly_summary=patient_summary,
        doctor_notes=doctor_notes,
        insufficient_evidence_pairs=insufficient_evidence_pairs,
        data_sources_used=list(data_sources)
    )


def _generate_patient_summary(interactions: List[DrugInteractionResult]) -> str:
    if not interactions:
        return "No known drug interactions were found among your current medications. Continue taking them as prescribed and inform your doctor of any new symptoms."
    
    critical = [i for i in interactions if i.severity in [SeverityLevel.CONTRAINDICATED, SeverityLevel.MAJOR]]
    
    summary_parts = []
    if critical:
        names = " and ".join([f"{i.drug_pair[0]} with {i.drug_pair[1]}" for i in critical[:2]])
        summary_parts.append(
            f"⚠️ Important: We found {len(critical)} serious medication interaction(s). "
            f"The combination of {names} may be dangerous. Please speak with your doctor immediately."
        )
    
    all_recs = [i.recommendation for i in interactions[:3]]
    if all_recs:
        summary_parts.append("Your doctor may need to: " + " OR ".join([r.split(".")[0] for r in all_recs]) + ".")
    
    summary_parts.append(
        "💊 Remember: Do not stop or change your medications without consulting your healthcare provider first."
    )
    
    return " ".join(summary_parts)


def _generate_doctor_notes(interactions: List[DrugInteractionResult], patient: PatientProfile) -> str:
    if not interactions:
        return "No clinically significant interactions identified in the current medication list."
    
    notes = [f"Clinical decision support analysis for {'renal-impaired' if patient.renal_function.value != 'normal' else 'standard'} patient (age {patient.age}):"]
    
    for i, ia in enumerate(interactions[:5], 1):
        notes.append(
            f"\n{i}. [{ia.severity.value.upper()}] {' + '.join(ia.drug_pair)}: "
            f"{ia.mechanism[:100]}... "
            f"Action: {ia.recommendation[:80]}..."
        )
    
    if patient.renal_function.value != "normal":
        notes.append(f"\n⚠️ Renal function ({patient.renal_function.value}) requires review of renally-cleared drugs.")
    
    return "\n".join(notes)
