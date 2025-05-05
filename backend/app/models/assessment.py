from datetime import datetime
from sqlalchemy import Column, String, JSON, Float, Enum as SQLEnum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.schemas.assessment import RiskLevel

class AssessmentRecord(BaseModel):
    """Database model for storing security assessment records"""
    __tablename__ = "assessment_records"

    # Organization and Project Info
    organization_name = Column(String(255), nullable=False, index=True)
    project_name = Column(String(255), nullable=False, index=True)
    
    # Assessment Results
    overall_score = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    ai_model_used = Column(String(50), nullable=False)
    
    # Detailed Results (stored as JSON)
    category_scores = Column(JSON, nullable=False)
    token_usage = Column(JSON, nullable=False)
    grounding_info = Column(JSON, nullable=True)
    
    # Relationships
    vulnerabilities = relationship("VulnerabilityRecord", back_populates="assessment")
    priority_actions = relationship("PriorityAction", back_populates="assessment")

class VulnerabilityRecord(BaseModel):
    """Database model for storing individual vulnerability findings"""
    __tablename__ = "vulnerability_records"

    assessment_id = Column(Integer, ForeignKey("assessment_records.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    recommendation = Column(Text, nullable=False)
    code_snippets = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=False, default=0.8)
    
    # Add unique constraint to prevent identical records (including confidence)
    __table_args__ = (
        UniqueConstraint(
            'assessment_id', 'title', 'description', 'severity', 
            'category', 'recommendation', 'code_snippets', 'confidence',
            name='uix_vulnerability_unique_content'
        ),
    )
    
    # Relationship
    assessment = relationship("AssessmentRecord", back_populates="vulnerabilities")

class PriorityAction(BaseModel):
    """Database model for storing prioritized actions from assessments"""
    __tablename__ = "priority_actions"

    assessment_id = Column(Integer, ForeignKey("assessment_records.id"), nullable=False)
    action_text = Column(Text, nullable=False)
    priority_order = Column(Integer, nullable=False)
    category = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")
    
    # Relationship
    assessment = relationship("AssessmentRecord", back_populates="priority_actions") 