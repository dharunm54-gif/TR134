"""
Pydantic schemas for Drug Interaction Screener
Defines all request/response models for the API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class SeverityLevel(str, Enum):
    CONTRAINDICATED = "Contraindicated"
    MAJOR = "Major"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


class RenalFunction(str, Enum):
    NORMAL = "normal"
    MILD_IMPAIRMENT = "mild_impairment"
    MODERATE_IMPAIRMENT = "moderate_impairment"
    SEVERE_IMPAIRMENT = "severe_impairment"
    ESRD = "esrd"


class HepaticFunction(str, Enum):
    NORMAL = "normal"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class DrugInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Drug name (brand or generic)")
    dosage: str = Field(..., description="Dosage with unit (e.g., '10mg', '500mcg')")
    frequency: str = Field(..., description="Administration frequency (e.g., 'twice daily', 'QID')")
    route: Optional[str] = Field(default="oral", description="Route of administration")
    
    @validator('name')
    def normalize_drug_name(cls, v):
        return v.strip().lower()


class PatientProfile(BaseModel):
    patient_id: Optional[str] = Field(default=None)
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    weight: float = Field(..., gt=0, le=500, description="Patient weight in kg")
    sex: Literal["male", "female", "other"] = "other"
    renal_function: RenalFunction = Field(default=RenalFunction.NORMAL)
    hepatic_function: HepaticFunction = Field(default=HepaticFunction.NORMAL)
    comorbidities: List[str] = Field(default=[], description="Active comorbidities")
    allergies: List[str] = Field(default=[], description="Known drug allergies")
    medications: List[DrugInput] = Field(..., min_items=1, max_items=30)


class InteractionEvidence(BaseModel):
    pubmed_id: Optional[str] = None
    drugbank_ref: Optional[str] = None
    source: str
    title: Optional[str] = None
    excerpt: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)


class DrugInteractionResult(BaseModel):
    drug_pair: List[str]
    severity: SeverityLevel
    mechanism: str
    mechanism_type: Literal[
        "CYP450_inhibition", "CYP450_induction", "receptor_conflict",
        "pharmacokinetic", "pharmacodynamic", "transporter", "unknown"
    ]
    clinical_risk: str
    clinical_manifestation: Optional[str] = None
    recommendation: str
    alternatives: List[str] = []
    dose_adjustment: Optional[str] = None
    monitoring_parameters: List[str] = []
    evidence: List[InteractionEvidence] = []
    onset: Optional[Literal["rapid", "delayed", "unknown"]] = None
    severity_score: float = Field(ge=0.0, le=10.0, default=0.0)


class InteractionRequest(BaseModel):
    patient: PatientProfile
    mode: Literal["doctor", "patient"] = "doctor"
    include_alternatives: bool = True
    include_evidence: bool = True


class RiskSummary(BaseModel):
    contraindicated_count: int = 0
    major_count: int = 0
    moderate_count: int = 0
    minor_count: int = 0
    overall_risk_score: float = Field(ge=0.0, le=10.0, default=0.0)
    highest_severity: SeverityLevel = SeverityLevel.UNKNOWN


class InteractionResponse(BaseModel):
    patient_id: Optional[str] = None
    analysis_id: str
    timestamp: str
    processing_time_ms: float
    medications_analyzed: List[str]
    interaction_count: int
    interactions: List[DrugInteractionResult]
    risk_summary: RiskSummary
    patient_friendly_summary: Optional[str] = None
    doctor_notes: Optional[str] = None
    insufficient_evidence_pairs: List[List[str]] = []
    data_sources_used: List[str] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: List[ChatMessage] = Field(default=[])
    context: Optional[Dict[str, Any]] = None
    mode: Literal["doctor", "patient"] = "doctor"
    analysis_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    citations: List[str] = []
    related_interactions: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class DashboardStats(BaseModel):
    total_patients: int
    high_risk_patients: int
    interactions_detected_today: int
    average_medications_per_patient: float
    severity_distribution: Dict[str, int]
    most_common_interactions: List[Dict[str, Any]]


class PatientRecord(BaseModel):
    patient_id: str
    name: Optional[str] = "Anonymous"
    age: int
    medication_count: int
    risk_level: SeverityLevel
    interaction_count: int
    last_analyzed: str
    alerts: List[str] = []
