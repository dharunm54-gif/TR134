"""
Patients Router - Patient management endpoints
"""

from fastapi import APIRouter, HTTPException
import logging
import uuid
from datetime import datetime
from typing import List
from models.schemas import PatientRecord, SeverityLevel

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store (use PostgreSQL in production)
PATIENT_STORE: List[dict] = [
    {
        "patient_id": "P-001",
        "name": "John Martinez",
        "age": 72,
        "medication_count": 7,
        "risk_level": "Major",
        "interaction_count": 3,
        "last_analyzed": "2026-04-16T08:30:00Z",
        "alerts": ["Warfarin + Aspirin", "Digoxin + Amiodarone"]
    },
    {
        "patient_id": "P-002",
        "name": "Sarah Thompson",
        "age": 64,
        "medication_count": 5,
        "risk_level": "Contraindicated",
        "interaction_count": 2,
        "last_analyzed": "2026-04-16T09:15:00Z",
        "alerts": ["Simvastatin + Clarithromycin"]
    },
    {
        "patient_id": "P-003",
        "name": "Robert Chen",
        "age": 58,
        "medication_count": 4,
        "risk_level": "Moderate",
        "interaction_count": 1,
        "last_analyzed": "2026-04-16T10:00:00Z",
        "alerts": ["Clopidogrel + Omeprazole"]
    },
    {
        "patient_id": "P-004",
        "name": "Emily Davis",
        "age": 45,
        "medication_count": 3,
        "risk_level": "Minor",
        "interaction_count": 0,
        "last_analyzed": "2026-04-16T11:30:00Z",
        "alerts": []
    },
    {
        "patient_id": "P-005",
        "name": "Michael Brown",
        "age": 81,
        "medication_count": 9,
        "risk_level": "Contraindicated",
        "interaction_count": 4,
        "last_analyzed": "2026-04-16T12:00:00Z",
        "alerts": ["Oxycodone + Diazepam", "Warfarin + Fluconazole"]
    },
]


@router.get("/patients", response_model=List[dict])
async def list_patients():
    """Return all patient records."""
    return PATIENT_STORE


@router.get("/patients/high-risk", response_model=List[dict])
async def list_high_risk_patients():
    """Return patients with Major or Contraindicated interactions."""
    return [
        p for p in PATIENT_STORE
        if p["risk_level"] in ["Major", "Contraindicated"]
    ]


@router.get("/patients/{patient_id}", response_model=dict)
async def get_patient(patient_id: str):
    """Get a specific patient record."""
    patient = next((p for p in PATIENT_STORE if p["patient_id"] == patient_id), None)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
