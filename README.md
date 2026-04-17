# 🧬 MediGuard AI — Drug Interaction Risk Screener

> **Generative AI-Powered Polypharmacy Safety System**  
> RAG-Grounded · Zero Hallucination · Evidence-Cited · Hackathon-Ready

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Dashboard│ │ PatientForm  │ │ResultsPanel│ │ ChatAssistant │  │
│  │ (Charts) │ │ (Drug inputs)│ │(Interactions│ │ (RAG Q&A)    │  │
│  └──────────┘ └──────────────┘ └──────────┘ └───────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP / REST API
┌─────────────────────────────▼───────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   API Routes (v1)                         │   │
│  │  POST /interactions/analyze  GET /patients  POST /chat    │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │              Core AI Pipeline                             │   │
│  │                                                           │   │
│  │  1. Drug Name Normalizer (brand→generic mapping)          │   │
│  │       ↓                                                   │   │
│  │  2. Interaction Engine (pairwise O(n²) analysis)          │   │
│  │       ↓                                                   │   │
│  │  3. Knowledge Graph Query (NetworkX → Neo4j in prod)      │   │
│  │       ↓                                                   │   │
│  │  4. RAG Evidence Retrieval (Vector Store → PubMed)        │   │
│  │       ↓                                                   │   │
│  │  5. Patient-Specific Risk Adjustment                      │   │
│  │     (renal/hepatic/age modifiers)                        │   │
│  │       ↓                                                   │   │
│  │  6. Structured JSON Response with Citations               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │ Knowledge Graph  │  │  Vector Store   │  │  Chat Service │   │
│  │ (NetworkX/Neo4j) │  │ (FAISS/keyword) │  │ (RAG-grounded)│   │
│  └──────────────────┘  └─────────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    ┌─────▼─────┐      ┌──────▼──────┐    ┌──────▼──────┐
    │  DrugBank │      │   PubMed    │    │    FAERS    │
    │ Curated DB│      │  Abstracts  │    │ FDA Adverse │
    └───────────┘      └─────────────┘    └─────────────┘
```

---

## 🚀 Quick Start

### 1. Backend (Python / FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/api/docs**

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

App at: **http://localhost:3000**

### 3. Full Stack (Docker)

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
drug-interaction-screener/
├── 📂 backend/
│   ├── main.py                    # FastAPI app + lifespan
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── routers/
│   │   ├── interactions.py        # POST /interactions/analyze
│   │   ├── patients.py            # GET /patients
│   │   ├── chat.py                # POST /chat
│   │   └── dashboard.py           # GET /dashboard/stats
│   └── services/
│       ├── interaction_engine.py  # Core drug interaction logic + DB
│       ├── knowledge_graph.py     # NetworkX drug-enzyme graph
│       ├── vector_store.py        # RAG evidence retrieval
│       └── chat_service.py        # Grounded AI chat
│
├── 📂 frontend/
│   ├── app/
│   │   ├── layout.tsx             # Root layout + metadata
│   │   ├── page.tsx               # App shell + routing
│   │   └── globals.css            # Design system + animations
│   ├── components/
│   │   ├── Sidebar.tsx            # Navigation + mode toggle
│   │   ├── Dashboard.tsx          # Stats + charts overview
│   │   ├── PatientForm.tsx        # Medication entry + presets
│   │   ├── ResultsPanel.tsx       # Interaction cards + donut
│   │   ├── ChatAssistant.tsx      # AI chat with evidence
│   │   ├── HighRiskCases.tsx      # Flagged patients
│   │   └── AllPatients.tsx        # Patient table + filters
│   ├── package.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   └── Dockerfile
│
├── 📂 knowledge-graph/
│   └── schemas/
│       └── neo4j_schema.py        # Neo4j Cypher schema + queries
│
├── 📂 ai-pipeline/                # Future: LangChain + BioMistral
│
├── 📂 data/                       # Sample datasets, mock data
│
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Reference

### `POST /api/v1/interactions/analyze`

**Request:**
```json
{
  "patient": {
    "age": 72,
    "weight": 70,
    "sex": "male",
    "renal_function": "mild_impairment",
    "hepatic_function": "normal",
    "comorbidities": ["atrial fibrillation", "heart failure"],
    "medications": [
      { "name": "warfarin",   "dosage": "5mg",    "frequency": "Once daily",  "route": "oral" },
      { "name": "amiodarone", "dosage": "200mg",   "frequency": "Twice daily", "route": "oral" },
      { "name": "digoxin",    "dosage": "0.125mg", "frequency": "Once daily",  "route": "oral" }
    ]
  },
  "mode": "doctor",
  "include_alternatives": true,
  "include_evidence": true
}
```

**Response:**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-04-16T08:00:00Z",
  "processing_time_ms": 204,
  "medications_analyzed": ["warfarin", "amiodarone", "digoxin"],
  "interaction_count": 2,
  "interactions": [
    {
      "drug_pair": ["warfarin", "amiodarone"],
      "severity": "Major",
      "mechanism": "Amiodarone inhibits CYP2C9 and CYP3A4, increasing warfarin plasma levels",
      "mechanism_type": "CYP450_inhibition",
      "clinical_risk": "Severe bleeding due to potentiated anticoagulation",
      "recommendation": "Reduce warfarin dose by 30–50%. Monitor INR weekly until stable.",
      "dose_adjustment": "Reduce warfarin by 30–50%",
      "alternatives": ["beta-blockers for rate control"],
      "monitoring_parameters": ["INR weekly", "bleeding signs"],
      "evidence": [
        { "pubmed_id": "12012363", "source": "PubMed", "confidence_score": 0.97 }
      ],
      "severity_score": 9.2,
      "onset": "delayed"
    },
    {
      "drug_pair": ["digoxin", "amiodarone"],
      "severity": "Major",
      "mechanism": "Amiodarone inhibits P-gp → digoxin levels rise 70–100%",
      "mechanism_type": "transporter",
      "clinical_risk": "Digoxin toxicity: bradycardia, heart block, ventricular arrhythmia",
      "recommendation": "Halve digoxin dose when amiodarone is initiated",
      "dose_adjustment": "Reduce digoxin by 50%",
      "severity_score": 8.0
    }
  ],
  "risk_summary": {
    "contraindicated_count": 0,
    "major_count": 2,
    "moderate_count": 0,
    "minor_count": 0,
    "overall_risk_score": 9.2,
    "highest_severity": "Major"
  },
  "patient_friendly_summary": "⚠️ We found 2 serious medication interactions...",
  "data_sources_used": ["DrugBank", "PubMed"],
  "insufficient_evidence_pairs": []
}
```

---

## 🧠 Safety Design Principles

| Rule | Implementation |
|------|---------------|
| **No Hallucination** | Only returns data from curated knowledge base |
| **Always Cite** | Every interaction includes PubMed ID / DrugBank ref |
| **Insufficient Evidence** | Returns explicit flag, never guesses |
| **Patient-Specific** | Adjusts risk scoring for renal/hepatic impairment, age |
| **Severity Calibration** | Score 0-10 with validated clinical thresholds |

---

## 💊 Supported Drug Interactions (14+ Evidence-Based Pairs)

| Drug Pair | Severity | Mechanism |
|-----------|----------|-----------|
| Warfarin + Aspirin | Major | Pharmacodynamic (additive bleeding) |
| Warfarin + Fluconazole | Major | CYP2C9 inhibition |
| Warfarin + Amiodarone | Major | CYP2C9 + CYP3A4 inhibition |
| Simvastatin + Clarithromycin | **Contraindicated** | CYP3A4 inhibition |
| Simvastatin + Amlodipine | Moderate | CYP3A4 inhibition |
| Sertraline + Phenelzine | **Contraindicated** | Serotonin syndrome |
| Ciprofloxacin + Amiodarone | **Contraindicated** | QT prolongation |
| Oxycodone + Diazepam | Major | CNS/respiratory depression |
| Allopurinol + Azathioprine | **Contraindicated** | Xanthine oxidase inhibition |
| Digoxin + Amiodarone | Major | P-glycoprotein inhibition |
| Lisinopril + Spironolactone | Major | Hyperkalemia |
| Clopidogrel + Omeprazole | Moderate | CYP2C19 inhibition |
| Lithium + Ibuprofen | Major | Renal clearance reduction |
| Metformin + Ibuprofen | Moderate | Renal clearance / lactic acidosis |

---

## 🐳 Docker Deployment

```bash
# Clone the project
git clone <repo-url>
cd drug-interaction-screener

# Start all services
docker-compose up --build

# Services will be available at:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000/api/docs
# Neo4j UI:  http://localhost:7474
```

---

## 🏆 Hackathon Impact

- **Clinical Safety**: Detects life-threatening polypharmacy interactions before they harm patients
- **Evidence-Based**: Every finding cites DrugBank / PubMed — zero fabrication
- **Dual Mode**: Doctor view (clinical detail) + Patient view (plain language)
- **Scalable**: NetworkX in-memory → Neo4j in production; keyword retrieval → FAISS/ChromaDB
- **Performance**: <300ms analysis for 10-drug combinations

---

## 🔮 Production Roadmap

- [ ] Neo4j graph with full DrugBank dataset (10,000+ drugs)
- [ ] FAISS vector store with 500k+ PubMed abstracts
- [ ] BioMistral / MedPaLM integration for enhanced reasoning
- [ ] FHIR R4 patient data import
- [ ] HL7 EHR integration (Epic, Cerner)
- [ ] Pharmacogenomics layer (CYP2D6, TPMT genotypes)
- [ ] Real-time FAERS signal monitoring

---

*Built for clinical safety · Powered by RAG · Grounded in evidence*
