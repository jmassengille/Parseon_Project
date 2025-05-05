from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class SecurityCategory(str, Enum):
    API_SECURITY = "API_SECURITY"
    PROMPT_SECURITY = "PROMPT_SECURITY"
    CONFIGURATION = "CONFIGURATION"
    ERROR_HANDLING = "ERROR_HANDLING"
    DATA_SECURITY = "DATA_SECURITY"
    MODEL_SECURITY = "MODEL_SECURITY"
    GENERAL_SECURITY = "GENERAL_SECURITY"

class ScanMode(str, Enum):
    COMPREHENSIVE = "COMPREHENSIVE"
    PROMPT_SECURITY = "PROMPT_SECURITY"
    API_SECURITY = "API_SECURITY"

class VulnerabilityFinding(BaseModel):
    """Represents a security finding from pattern matching or AI analysis"""
    id: str = Field(..., description="Unique identifier for the finding")
    title: str = Field(..., description="Title of the vulnerability")
    description: str = Field(..., description="Detailed description of the vulnerability")
    severity: str = Field(..., description="Severity level of the vulnerability")
    category: str = Field(..., description="Category of the vulnerability")
    code_snippets: List[str] = Field(default_factory=list, description="Relevant code snippets")
    recommendation: str = Field(..., description="Recommended remediation steps")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score of the finding")
    validation_info: Optional[Dict[str, Any]] = Field(default=None, description="Additional validation information")

class SecurityScore(BaseModel):
    """Represents a security score for a specific category"""
    score: float = Field(..., ge=0.0, le=100.0, description="Score for this category")
    findings: List[str] = Field(default_factory=list, description="Key findings in this category")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for this category")

    def dict(self, *args, **kwargs):
        """Custom dict serialization"""
        return {
            "score": self.score,
            "findings": self.findings,
            "recommendations": self.recommendations
        }

    class Config:
        json_encoders = {
            'SecurityScore': lambda v: v.dict()
        }

class AssessmentResult(BaseModel):
    """Represents the complete results of a security assessment"""
    project_id: str = Field(..., description="Unique identifier for the assessment")
    findings: List[VulnerabilityFinding] = Field(default_factory=list, description="List of vulnerability findings")
    summary: str = Field(..., description="Executive summary of the assessment")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="Overall risk score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the assessment")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional assessment metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_123",
                "findings": [
                    {
                        "title": "Critical Prompt Injection Risk",
                        "description": "Multiple endpoints vulnerable to prompt injection",
                        "risk_level": "CRITICAL",
                        "category": "prompt_security",
                        "confidence": 0.92,
                        "remediation": "Implement comprehensive input validation",
                        "affected_components": ["api", "model_pipeline"]
                    }
                ],
                "summary": "Critical security issues found in AI implementation",
                "risk_score": 8.5,
                "metadata": {
                    "scan_duration": "120s",
                    "components_analyzed": ["code", "config", "architecture"]
                }
            }
        }

class SecurityAssessmentResult(BaseModel):
    """Represents the complete results of a security assessment"""
    id: Optional[int] = Field(None, description="Database ID of the assessment")
    organization_name: str = Field(..., description="Name of the organization")
    project_name: str = Field(..., description="Name of the project")
    timestamp: datetime = Field(..., description="Timestamp of the assessment")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall security score")
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    category_scores: Dict[str, SecurityScore] = Field(..., description="Scores for each security category")
    vulnerabilities: List[VulnerabilityFinding] = Field(..., description="List of vulnerability findings")
    priority_actions: List[str] = Field(..., description="Prioritized action items")
    ai_model_used: str = Field(..., description="AI model used for analysis")
    token_usage: Dict[str, int] = Field(..., description="Token usage statistics")
    environment: Optional[str] = Field(None, description="Environment of the assessment")
    data_sensitivity: Optional[str] = Field(None, description="Data sensitivity of the assessment")
    grounding_info: Optional[Dict[str, Any]] = Field(None, description="Additional grounding information")

    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "Example Corp",
                "project_name": "AI Chat Bot",
                "timestamp": "2024-03-20T10:00:00Z",
                "overall_score": 75.5,
                "overall_risk_level": "HIGH",
                "category_scores": {
                    "api_security": {
                        "score": 80.0,
                        "findings": ["Missing rate limiting"],
                        "recommendations": ["Implement rate limiting"]
                    }
                },
                "vulnerabilities": [
                    {
                        "title": "Critical Prompt Injection Risk",
                        "description": "Multiple endpoints vulnerable to prompt injection",
                        "risk_level": "CRITICAL",
                        "category": "prompt_security",
                        "remediation": "Implement input validation",
                        "confidence": 0.95
                    }
                ],
                "priority_actions": [
                    "[CRITICAL] Implement input validation",
                    "[HIGH] Add rate limiting"
                ],
                "ai_model_used": "gpt-3.5-turbo",
                "token_usage": {
                    "prompt_tokens": 1000,
                    "completion_tokens": 500
                }
            }
        }

class GroundingInfo(BaseModel):
    confidence_score: float
    validation_notes: List[str]
    missing_patterns: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "confidence_score": 0.95,
                "validation_notes": ["All patterns validated", "No missing patterns"],
                "missing_patterns": []
            }
        } 