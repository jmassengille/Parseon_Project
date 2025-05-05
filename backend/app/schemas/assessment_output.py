from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VulnerabilityFinding(BaseModel):
    id: str = Field(..., description="Unique identifier for the finding")
    title: str = Field(..., description="Title of the vulnerability")
    description: str = Field(..., description="Detailed description of the vulnerability")
    severity: str = Field(..., description="Severity level of the vulnerability")
    category: str = Field(..., description="Category of the vulnerability")
    code_snippets: List[str] = Field(default_factory=list, description="Relevant code snippets")
    recommendation: str = Field(..., description="Recommended remediation steps")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score of the finding")

class SecurityScore(BaseModel):
    score: float = Field(..., ge=0, le=100, description="Security score (0-100)")
    findings: List[str] = Field(default_factory=list, description="Key findings that affected the score")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")

class SecurityAssessmentResult(BaseModel):
    """
    Output schema for security assessment results.
    
    This model structures the assessment output with:
    - Overall scores and risk levels
    - Category-specific scores
    - Detailed vulnerability findings
    - Prioritized action items
    - Assessment metadata (model used, token usage)
    
    Scores range from 0-100, with risk levels of CRITICAL, HIGH, MEDIUM, and LOW.
    """
    id: Optional[int] = Field(None, description="Database ID of the assessment")
    organization_name: str
    project_name: str
    timestamp: datetime
    
    # Overall Scores
    overall_score: float = Field(..., ge=0, le=100, description="Overall security score")
    overall_risk_level: RiskLevel
    
    # Category Scores
    category_scores: Dict[str, SecurityScore]
    
    # Findings and Actions
    vulnerabilities: List[VulnerabilityFinding]
    priority_actions: List[str]
    
    # Metadata
    ai_model_used: str = Field(..., description="AI model used for analysis")
    token_usage: Dict[str, int]
    grounding_info: Optional[Dict[str, Any]] = Field(None, description="Additional grounding information") 