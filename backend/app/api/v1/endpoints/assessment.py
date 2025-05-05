from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.assessment_input import SecurityAssessmentInput
from app.schemas.assessment import SecurityAssessmentResult, SecurityScore
from app.services.assessment_service import SecurityAssessmentService
from app.crud.assessment import AssessmentCRUD
from app.db.session import get_db
from app.core.exceptions import AssessmentError, ValidationError
from app.core.rate_limiter import rate_limit
from app.core.config import settings
from app.core.vector_store_singleton import get_vector_store
from app.services.vector_store import VectorStore
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

def _transform_assessment_result(result: SecurityAssessmentResult) -> Dict[str, Any]:
    """Transform backend assessment result to frontend format"""
    # Calculate security score breakdown
    security_score_breakdown = {
        "API_SECURITY": result.category_scores.get("API_SECURITY", SecurityScore(score=0, findings=[], recommendations=[])).score,
        "PROMPT_SECURITY": result.category_scores.get("PROMPT_SECURITY", SecurityScore(score=0, findings=[], recommendations=[])).score,
        "CONFIGURATION": result.category_scores.get("CONFIGURATION", SecurityScore(score=0, findings=[], recommendations=[])).score,
        "ERROR_HANDLING": result.category_scores.get("ERROR_HANDLING", SecurityScore(score=0, findings=[], recommendations=[])).score
    }

    # Calculate overall score as weighted average of category scores
    category_weights = {
        "API_SECURITY": 0.35,
        "PROMPT_SECURITY": 0.35,
        "CONFIGURATION": 0.15,
        "ERROR_HANDLING": 0.15
    }
    
    overall_score = sum(
        security_score_breakdown[category] * weight
        for category, weight in category_weights.items()
    )
    overall_score = round(overall_score, 1)  # Round to 1 decimal place

    # Transform findings to match frontend format
    findings = []
    for finding in result.vulnerabilities:
        findings.append({
            "category": finding.category,
            "severity": finding.severity.upper(),  # Ensure uppercase severity
            "title": finding.title,
            "description": finding.description,
            "recommendation": finding.recommendation
        })

    # Create a summary based on findings
    summary = f"Security assessment for {result.project_name} completed with {len(findings)} findings."
    if findings:
        critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in findings if f["severity"] == "HIGH")
        summary += f" Found {critical_count} critical and {high_count} high severity issues."

    return {
        "project_name": result.project_name,
        "timestamp": result.timestamp.isoformat(),
        "overall_score": overall_score,  # Use calculated overall score
        "risk_level": result.overall_risk_level.value,  # Use enum value
        "summary": summary,
        "findings": findings,
        "recommendations": result.priority_actions,
        "security_score_breakdown": security_score_breakdown
    }

@router.post("/assess", response_model=Dict[str, Any])
async def assess_security(
    input_data: SecurityAssessmentInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    vector_store: VectorStore = Depends(get_vector_store),
    _: None = rate_limit(requests=5, period=60) if settings.ENVIRONMENT == "production" else None
):
    """
    Perform a security assessment of AI implementation and store results.
    
    Rate limited to 5 requests per minute per client in production.
    
    This endpoint:
    1. Accepts configuration files, implementation details, and architectural information
    2. Analyzes security risks in AI systems
    3. Stores the assessment results in the database and vector store
    4. Returns the complete assessment result
    """
    try:
        # Initialize the assessment service
        service = SecurityAssessmentService()
        await service.initialize()
        
        # Perform the assessment
        result = await service.analyze_input(input_data)
        
        # Store the assessment result in the background
        background_tasks.add_task(
            store_assessment_result,
            db=db,
            result=result,
            vector_store=vector_store
        )
        
        # Transform result to frontend format
        transformed_result = _transform_assessment_result(result)
        
        logger.info(f"Assessment completed for {input_data.organization_name}/{input_data.project_name}")
        return transformed_result
        
    except ValidationError as e:
        logger.error(f"Validation error in assess_security: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except AssessmentError as e:
        logger.error(f"Assessment error in assess_security: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in assess_security: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during assessment")

@router.get("/assessments/{assessment_id}", response_model=Dict[str, Any])
async def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    _: None = rate_limit(requests=30, period=60)  # 30 requests per minute for retrieval
):
    """Get a specific assessment result by ID. Rate limited to 30 requests per minute."""
    try:
        assessment = await AssessmentCRUD.get_assessment(db, assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return _transform_assessment_result(assessment)
    except Exception as e:
        logger.error(f"Error retrieving assessment {assessment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving assessment")

@router.get("/assessments/organization/{organization_name}", response_model=List[Dict[str, Any]])
async def get_organization_assessments(
    organization_name: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: None = rate_limit(requests=20, period=60)  # 20 requests per minute for organization listings
):
    """Get all assessments for an organization. Rate limited to 20 requests per minute."""
    try:
        assessments = await AssessmentCRUD.get_assessments_by_org(
            db,
            organization_name,
            skip=skip,
            limit=limit
        )
        return [_transform_assessment_result(assessment) for assessment in assessments]
    except Exception as e:
        logger.error(f"Error retrieving assessments for {organization_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving assessments")

@router.get("/assessments/project/{project_name}", response_model=List[Dict[str, Any]])
async def get_project_assessments(
    project_name: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: None = rate_limit(requests=20, period=60)  # 20 requests per minute for project listings
):
    """Get all assessments for a project. Rate limited to 20 requests per minute."""
    try:
        assessments = await AssessmentCRUD.get_assessments_by_project(
            db,
            project_name,
            skip=skip,
            limit=limit
        )
        return [_transform_assessment_result(assessment) for assessment in assessments]
    except Exception as e:
        logger.error(f"Error retrieving assessments for project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving assessments")

@router.post("/search/similar", response_model=List[Dict[str, Any]])
async def search_similar_findings(
    query: Dict[str, str],
    vector_store: VectorStore = Depends(get_vector_store),
    _: None = rate_limit(requests=20, period=60)  # 20 requests per minute
):
    """
    Search for similar security findings using semantic search.
    
    This endpoint:
    1. Takes a search query as input
    2. Finds semantically similar security findings
    3. Returns a list of relevant findings with similarity scores
    
    Example request:
    {
        "query": "prompt injection vulnerability in API endpoints"
    }
    """
    try:
        # Get query text
        query_text = query.get("query")
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")
            
        # Initialize embedding service
        from app.services.embeddings_service import EmbeddingsService
        embedding_service = EmbeddingsService()
        
        # Generate embedding for query
        query_embedding = embedding_service.get_embedding(query_text)
        
        # Search for similar documents
        results = await vector_store.search_similar(
            query_embedding=query_embedding,
            limit=10,
            score_threshold=0.7
        )
        
        # Transform results
        transformed_results = []
        for result in results:
            transformed_results.append({
                "id": result["id"],
                "title": result["metadata"]["title"],
                "severity": result["metadata"]["severity"],
                "category": result["metadata"]["category"],
                "confidence": result["metadata"]["confidence"],
                "content": result["content"],
                "similarity_score": result["score"],
                "created_at": result["created_at"].isoformat()
            })
        
        logger.info(f"Found {len(transformed_results)} similar findings for query: {query_text}")
        return transformed_results
        
    except Exception as e:
        logger.error(f"Error searching for similar findings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error searching for similar findings")

async def store_assessment_result(db: Session, result: SecurityAssessmentResult, vector_store: VectorStore = None):
    """Store assessment result in the database and vector store"""
    try:
        # Initialize assessment service
        service = SecurityAssessmentService()
        await service.initialize()
        
        # Store the assessment
        await service.store_assessment_result(result, db, vector_store)
    except Exception as e:
        logger.error(f"Error storing assessment result: {str(e)}", exc_info=True)
        # Don't raise the exception as this is a background task 