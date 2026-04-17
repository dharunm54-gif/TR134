"""
Drug Interactions Router - Main API endpoint
"""

from fastapi import APIRouter, HTTPException, Depends, Request
import logging
from models.schemas import InteractionRequest, InteractionResponse
from services.interaction_engine import analyze_interactions

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/interactions/analyze", response_model=InteractionResponse)
async def analyze_drug_interactions(
    request_body: InteractionRequest,
    request: Request
):
    """
    Analyze drug-drug interactions for a patient's medication list.
    
    Returns structured interaction data with:
    - Severity levels (Contraindicated/Major/Moderate/Minor)
    - Mechanism of interaction
    - Clinical recommendations
    - Alternative medications
    - Evidence citations
    """
    try:
        result = await analyze_interactions(
            patient=request_body.patient,
            include_evidence=request_body.include_evidence
        )
        return result
    except Exception as e:
        logger.error(f"Interaction analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/interactions/drugs")
async def get_supported_drugs():
    """Return list of drugs in the knowledge base."""
    from services.interaction_engine import DRUG_INTERACTION_DB, normalize_drug_name
    drugs = set()
    for pair in DRUG_INTERACTION_DB.keys():
        drugs.add(pair[0])
        drugs.add(pair[1])
    return {"supported_drugs": sorted(list(drugs)), "count": len(drugs)}


@router.get("/interactions/drug/{drug_name}")
async def get_drug_interactions(drug_name: str, request: Request):
    """Get all known interactions for a specific drug."""
    kg = request.app.state.kg_service
    interactions = await kg.get_drug_interactions(drug_name.lower())
    cyp_profile = await kg.get_cyp_profile(drug_name.lower())
    
    return {
        "drug": drug_name.lower(),
        "interactions": interactions,
        "cyp_profile": cyp_profile
    }
