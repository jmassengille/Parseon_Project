from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.assessment import SecurityAssessmentResult, VulnerabilityFinding

class AssessmentCRUD:
    @staticmethod
    async def create_assessment(
        db: AsyncSession,
        assessment_result: SecurityAssessmentResult
    ) -> 'AssessmentRecord':
        """Create a new assessment record with related vulnerabilities and actions"""
        from app.models.assessment import AssessmentRecord, VulnerabilityRecord, PriorityAction
        
        # Convert category scores to JSON-serializable format
        category_scores = {
            category: score.dict()
            for category, score in assessment_result.category_scores.items()
        }
        
        # Create main assessment record
        db_assessment = AssessmentRecord(
            organization_name=assessment_result.organization_name,
            project_name=assessment_result.project_name,
            overall_score=assessment_result.overall_score,
            risk_level=assessment_result.overall_risk_level,
            ai_model_used=assessment_result.ai_model_used,
            category_scores=category_scores,
            token_usage=assessment_result.token_usage,
            grounding_info=assessment_result.grounding_info
        )
        db.add(db_assessment)
        await db.flush()  # Get ID without committing
        
        # Create vulnerability records
        for finding in assessment_result.vulnerabilities:
            db_vulnerability = VulnerabilityRecord(
                assessment_id=db_assessment.id,
                title=finding.title,
                description=finding.description,
                severity=finding.severity,
                category=finding.category,
                recommendation=finding.recommendation,
                code_snippets=finding.code_snippets,
                confidence=finding.confidence
            )
            db.add(db_vulnerability)
        
        # Create priority action records
        for i, action in enumerate(assessment_result.priority_actions):
            db_action = PriorityAction(
                assessment_id=db_assessment.id,
                action_text=action,
                priority_order=i + 1,
                category=action.split("]")[0].strip("[") if "]" in action else None
            )
            db.add(db_action)
        
        await db.commit()
        await db.refresh(db_assessment)
        return db_assessment

    @staticmethod
    async def get_assessment(
        db: AsyncSession,
        assessment_id: int
    ) -> 'Optional[AssessmentRecord]':
        """Get an assessment record by ID"""
        from app.models.assessment import AssessmentRecord
        result = await db.execute(
            select(AssessmentRecord).filter(AssessmentRecord.id == assessment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_assessments_by_org(
        db: AsyncSession,
        organization_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> 'List[AssessmentRecord]':
        """Get all assessment records for an organization"""
        from app.models.assessment import AssessmentRecord
        result = await db.execute(
            select(AssessmentRecord)
            .filter(AssessmentRecord.organization_name == organization_name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_assessments_by_project(
        db: AsyncSession,
        project_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> 'List[AssessmentRecord]':
        """Get all assessment records for a project"""
        from app.models.assessment import AssessmentRecord
        result = await db.execute(
            select(AssessmentRecord)
            .filter(AssessmentRecord.project_name == project_name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_assessment_status(
        db: AsyncSession,
        assessment_id: int,
        updates: Dict[str, Any]
    ) -> 'Optional[AssessmentRecord]':
        """Update specific fields of an assessment record"""
        from app.models.assessment import AssessmentRecord
        result = await db.execute(
            select(AssessmentRecord).filter(AssessmentRecord.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        
        if assessment:
            for key, value in updates.items():
                if hasattr(assessment, key):
                    setattr(assessment, key, value)
            
            await db.commit()
            await db.refresh(assessment)
        
        return assessment

    @staticmethod
    async def delete_assessment(
        db: AsyncSession,
        assessment_id: int
    ) -> bool:
        """Delete an assessment record and its related records"""
        from app.models.assessment import AssessmentRecord
        result = await db.execute(
            select(AssessmentRecord).filter(AssessmentRecord.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        
        if assessment:
            await db.delete(assessment)  # This will cascade to related records
            await db.commit()
            return True
        return False 