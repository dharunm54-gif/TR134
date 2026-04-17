"""
Dashboard Router - Analytics and statistics endpoints
"""

from fastapi import APIRouter, Request
import logging
from models.schemas import DashboardStats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Return aggregate statistics for the dashboard."""
    return {
        "total_patients": 5,
        "high_risk_patients": 3,
        "interactions_detected_today": 10,
        "average_medications_per_patient": 5.6,
        "severity_distribution": {
            "Contraindicated": 2,
            "Major": 4,
            "Moderate": 3,
            "Minor": 1
        },
        "most_common_interactions": [
            {"pair": "Warfarin + Aspirin", "count": 12, "severity": "Major"},
            {"pair": "Simvastatin + Clarithromycin", "count": 8, "severity": "Contraindicated"},
            {"pair": "Clopidogrel + Omeprazole", "count": 7, "severity": "Moderate"},
            {"pair": "Oxycodone + Diazepam", "count": 5, "severity": "Major"},
            {"pair": "Lisinopril + Spironolactone", "count": 4, "severity": "Major"},
        ],
        "interactions_trend": [
            {"date": "2026-04-10", "count": 3},
            {"date": "2026-04-11", "count": 5},
            {"date": "2026-04-12", "count": 2},
            {"date": "2026-04-13", "count": 7},
            {"date": "2026-04-14", "count": 4},
            {"date": "2026-04-15", "count": 6},
            {"date": "2026-04-16", "count": 10},
        ]
    }


@router.get("/dashboard/graph-stats")
async def get_graph_stats(request: Request):
    """Return knowledge graph statistics."""
    kg = request.app.state.kg_service
    return await kg.get_graph_stats()
