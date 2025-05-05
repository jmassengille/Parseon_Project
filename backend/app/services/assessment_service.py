from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.schemas.assessment_input import SecurityAssessmentInput, ConfigType
from app.schemas.assessment import (
    SecurityAssessmentResult,
    SecurityScore,
    VulnerabilityFinding,
    RiskLevel,
    SecurityCategory,
    ScanMode
)
from app.core.finding_validator import FindingValidator
from app.core.base_model_analyzer import BaseModelAnalyzer
from app.core.knowledge_base import KnowledgeBase
import json
import logging
from pydantic import ValidationError
import re
from sqlalchemy.orm import Session
from app.services.embeddings_service import EmbeddingsService
from app.crud.assessment import AssessmentCRUD
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)

class SecurityAssessmentService:
    """
    Core service for performing AI security assessments.
    
    This service combines base model analysis and finding validation to evaluate security risks
    in AI implementations. It examines:
    - API security (35% of score)
    - Prompt security (35% of score)
    - Configuration security (15% of score)
    - Error handling (15% of score)
    """
    
    def __init__(self):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-16k")
        self.token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        
        # Replace AI analyzer with base model analyzer
        self.base_analyzer = BaseModelAnalyzer()
        
        # Replace grounding system with finding validator
        self.knowledge_base = KnowledgeBase()
        self.finding_validator = FindingValidator(knowledge_base=self.knowledge_base)
        
        # Risk weights for score calculation
        self.risk_weights = {
            RiskLevel.CRITICAL: 1.0,
            RiskLevel.HIGH: 0.7,
            RiskLevel.MEDIUM: 0.4,
            RiskLevel.LOW: 0.1
        }
        
        # Category weights for overall score
        self.category_weights = {
            SecurityCategory.API_SECURITY: 0.35,
            SecurityCategory.PROMPT_SECURITY: 0.35,
            SecurityCategory.CONFIGURATION: 0.15,
            SecurityCategory.ERROR_HANDLING: 0.15
        }

    def _is_similar_finding(self, finding1: VulnerabilityFinding, finding2: VulnerabilityFinding) -> bool:
        """Check if two findings are semantically similar"""
        # Check if they're in the same category
        if finding1.category != finding2.category:
            return False
            
        # Check for exact title match
        if finding1.title == finding2.title:
            return True
            
        # Check for semantic similarity in titles
        title1 = finding1.title.lower()
        title2 = finding2.title.lower()
        
        # Common variations to check
        variations = {
            "rate limit": ["rate limiting", "rate limiting controls", "rate limiting mechanism"],
            "input validation": ["input validation", "input sanitization", "input verification"],
            "error handling": ["error handling", "exception handling", "error management"],
            "authentication": ["authentication", "auth", "authentication mechanism"],
            "authorization": ["authorization", "access control", "permission"],
            "api key": ["api key", "api keys", "api token", "api tokens"],
            "model configuration": ["model configuration", "model settings", "model parameters"]
        }
        
        # Check if titles contain similar key phrases
        for key, values in variations.items():
            if any(v in title1 for v in values) and any(v in title2 for v in values):
                return True
                
        return False

    async def analyze_input(self, assessment_input: SecurityAssessmentInput) -> SecurityAssessmentResult:
        """
        Perform comprehensive security assessment using base model analysis and finding validation.
        
        Args:
            assessment_input: SecurityAssessmentInput object containing assessment details
            
        Returns:
            SecurityAssessmentResult object with assessment findings
            
        Raises:
            ValidationError: If input validation fails
            ValueError: If required fields are missing
            Exception: For other processing errors
        """
        try:
            # Validate input
            self._validate_input(assessment_input)
            
            # Set category weights based on scan mode
            self._set_category_weights_for_mode(assessment_input.scan_mode)
            
            # Initialize findings lists
            all_findings = []
            
            # Initialize finding validator
            await self.finding_validator.initialize()
            
            # Analyze implementation details using base analyzer
            if assessment_input.implementation_details:
                logger.info("Starting implementation details analysis")
                for component, code in assessment_input.implementation_details.items():
                    logger.info(f"Analyzing component: {component}")
                    
                    # Get findings from base model analysis
                    findings = await self.base_analyzer.analyze_code(code, component)
                    
                    # Validate findings against known patterns
                    validated_findings = await self.finding_validator.validate_findings(findings)
                    
                    logger.info(f"Found {len(validated_findings)} issues in {component}")
                    for f in validated_findings:
                        validation_status = "✓" if f.validation_info and f.validation_info.get("validated", False) else "?"
                        logger.info(f"Finding: {f.title} ({f.severity}) - confidence: {f.confidence} validation: {validation_status}")
                        
                    # Add to all findings, checking for duplicates
                    for finding in validated_findings:
                        if not any(self._is_similar_finding(finding, existing) for existing in all_findings):
                            all_findings.append(finding)
                        else:
                            logger.info(f"Skipping duplicate finding: {finding.title}")
                            
                logger.info("Completed implementation details analysis")
            
            # Analyze configuration using base analyzer
            if assessment_input.configs:
                logger.info("Starting configuration analysis")
                for config_type, config_content in assessment_input.configs.items():
                    logger.info(f"Analyzing config: {config_type}")
                    
                    # Get findings from base model analysis
                    findings = await self.base_analyzer.analyze_config(config_content)
                    
                    # Validate findings against known patterns
                    validated_findings = await self.finding_validator.validate_findings(findings)
                    
                    logger.info(f"Found {len(validated_findings)} issues in {config_type} config")
                    for f in validated_findings:
                        validation_status = "✓" if f.validation_info and f.validation_info.get("validated", False) else "?"
                        logger.info(f"Finding: {f.title} ({f.severity}) - confidence: {f.confidence} validation: {validation_status}")
                        
                    # Add to all findings, checking for duplicates
                    for finding in validated_findings:
                        if not any(self._is_similar_finding(finding, existing) for existing in all_findings):
                            all_findings.append(finding)
                        else:
                            logger.info(f"Skipping duplicate finding: {finding.title}")
                            
                logger.info("Completed configuration analysis")
            
            # Print summary of findings
            logger.info(f"Analysis complete - found {len(all_findings)} total findings")
            
            # Note: We no longer need the separate _analyze_with_ai method
            # since we're directly using the base model analyzer
            
            # Create the assessment result
            assessment_result = SecurityAssessmentResult(
                organization_name=assessment_input.organization_name,
                project_name=assessment_input.project_name,
                timestamp=datetime.now(),
                overall_score=self._calculate_overall_score(all_findings),
                overall_risk_level=self._calculate_risk_level(self._calculate_overall_score(all_findings)),
                vulnerabilities=all_findings,
                category_scores=self._calculate_category_scores(all_findings),
                priority_actions=self._prioritize_actions(all_findings),
                ai_model_used=self.model,
                token_usage=self.token_usage
            )
            
            logger.info(f"Assessment result created with score: {assessment_result.overall_score}, risk level: {assessment_result.overall_risk_level}")
            logger.info(f"Found {len(all_findings)} vulnerabilities across {len(assessment_result.category_scores)} categories")
            
            # Update token usage
            self.token_usage["prompt_tokens"] += self.base_analyzer.token_usage["prompt_tokens"]
            self.token_usage["completion_tokens"] += self.base_analyzer.token_usage["completion_tokens"]
            logger.debug(f"Token usage: {self.token_usage['prompt_tokens']} prompt, {self.token_usage['completion_tokens']} completion")
            
            # Return the assessment result
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in security assessment: {str(e)}")
            raise

    def _validate_input(self, input_data: SecurityAssessmentInput) -> None:
        """Validate assessment input data"""
        if not input_data.organization_name or not input_data.project_name:
            raise ValueError("Organization name and project name are required")
            
        if not input_data.configs and not input_data.implementation_details:
            raise ValueError("At least one of configs or implementation details must be provided")
            
        # Validate configs if present
        if input_data.configs:
            for config_type, content in input_data.configs.items():
                if not content:
                    raise ValueError(f"Empty content for config type: {config_type}")
                    
        # Validate implementation details if present
        if input_data.implementation_details:
            for component, code in input_data.implementation_details.items():
                if not code:
                    raise ValueError(f"Empty code for component: {component}")

    def _prepare_analysis_context(self, input_data: SecurityAssessmentInput) -> str:
        """Prepare comprehensive context for AI analysis"""
        context_parts = []
        
        # Add organization and project info
        context_parts.append(f"Organization: {input_data.organization_name}")
        context_parts.append(f"Project: {input_data.project_name}")
        
        # Add configuration details
        if input_data.configs:
            context_parts.append("\nConfiguration Details:")
            for config_type, content in input_data.configs.items():
                context_parts.append(f"\n{config_type.value}:")
                context_parts.append(content)
        
        # Add implementation details
        if input_data.implementation_details:
            context_parts.append("\nImplementation Details:")
            for component, code in input_data.implementation_details.items():
                context_parts.append(f"\n{component}:")
                context_parts.append(code)
        
        # Add architecture description
        if input_data.architecture_description:
            context_parts.append("\nArchitecture Description:")
            context_parts.append(input_data.architecture_description)
        
        return "\n".join(context_parts)

    def _sanitize_category(self, category: str) -> str:
        """Sanitize category string to an expected enum value"""
        category_mapping = {
            "prompt": "PROMPT_SECURITY",
            "prompt_security": "PROMPT_SECURITY",
            "prompt security": "PROMPT_SECURITY",
            "injection": "PROMPT_SECURITY",
            "prompt injection": "PROMPT_SECURITY",
            
            "api": "API_SECURITY",
            "api_security": "API_SECURITY",
            "api security": "API_SECURITY",
            "authentication": "API_SECURITY",
            "authorization": "API_SECURITY",
            
            "config": "CONFIGURATION",
            "configuration": "CONFIGURATION",
            "settings": "CONFIGURATION",
            
            "error": "ERROR_HANDLING",
            "error_handling": "ERROR_HANDLING",
            "exception": "ERROR_HANDLING"
        }
        
        category_lower = category.lower()
        
        # Try direct matches
        for pattern, mapped_value in category_mapping.items():
            if pattern in category_lower:
                return mapped_value
                
        # Default to API_SECURITY
        return "API_SECURITY"

    def _sanitize_severity(self, severity: str) -> str:
        """Sanitize severity string to an expected enum value"""
        severity_mapping = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "severe": "HIGH",
            "medium": "MEDIUM",
            "moderate": "MEDIUM",
            "low": "LOW",
            "minor": "LOW",
            "info": "LOW",
            "informational": "LOW"
        }
        
        severity_lower = severity.lower()
        
        # Try direct matches
        for pattern, mapped_value in severity_mapping.items():
            if pattern in severity_lower:
                return mapped_value
                
        # Default to MEDIUM
        return "MEDIUM"

    def _set_category_weights_for_mode(self, scan_mode: ScanMode) -> None:
        """Adjust category weights based on the scan mode"""
        if scan_mode == ScanMode.PROMPT_SECURITY:
            self.category_weights = {
                SecurityCategory.API_SECURITY: 0.15,
                SecurityCategory.PROMPT_SECURITY: 0.65,  # Increased weight
                SecurityCategory.CONFIGURATION: 0.1,
                SecurityCategory.ERROR_HANDLING: 0.1
            }
        elif scan_mode == ScanMode.API_SECURITY:
            self.category_weights = {
                SecurityCategory.API_SECURITY: 0.65,  # Increased weight
                SecurityCategory.PROMPT_SECURITY: 0.15,
                SecurityCategory.CONFIGURATION: 0.1,
                SecurityCategory.ERROR_HANDLING: 0.1
            }
        else:  # COMPREHENSIVE mode
            self.category_weights = {
                SecurityCategory.API_SECURITY: 0.35,
                SecurityCategory.PROMPT_SECURITY: 0.35,
                SecurityCategory.CONFIGURATION: 0.15,
                SecurityCategory.ERROR_HANDLING: 0.15
            }

    def _calculate_overall_score(self, findings: List[VulnerabilityFinding]) -> float:
        """Calculate overall security score based on findings"""
        # Start with a perfect score
        base_score = 100
        
        # Calculate penalty for each finding
        total_penalty = 0
        for finding in findings:
            severity = finding.severity
            
            # Get the severity weight
            risk_weight = self.risk_weights.get(severity, 0.5)
            
            # Get the category weight
            category_weight = self.category_weights.get(finding.category, 0.25)
            
            # Calculate penalty based on severity and category weights
            penalty = 10 * risk_weight * category_weight * finding.confidence
            total_penalty += penalty
        
        # Apply penalty to base score
        final_score = max(0, base_score - total_penalty)
        
        return round(final_score, 1)

    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Determine overall risk level based on score"""
        if score < 50:
            return RiskLevel.CRITICAL
        elif score < 70:
            return RiskLevel.HIGH
        elif score < 85:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_category_scores(self, findings: List[VulnerabilityFinding]) -> Dict[str, SecurityScore]:
        """Calculate security scores for each category"""
        category_scores = {}
        
        # Initialize scores for each category
        for category in SecurityCategory:
            category_scores[category] = {
                "score": 100,  # Start with perfect score
                "findings": [],
                "recommendations": []
            }
        
        # Apply penalty for each finding
        for finding in findings:
            category = finding.category
            
            # Get the severity weight
            risk_weight = self.risk_weights.get(finding.severity, 0.5)
            
            # Calculate penalty based on severity
            penalty = 10 * risk_weight * finding.confidence
            
            # Ensure category exists in the dictionary
            if category not in category_scores:
                category_scores[category] = {
                    "score": 100,
                    "findings": [],
                    "recommendations": []
                }
                
            # Apply penalty to the category score
            category_scores[category]["score"] = max(0, category_scores[category]["score"] - penalty)
            
            # Add finding title to the category
            category_scores[category]["findings"].append(finding.title)
            
            # Add recommendation to the category
            if finding.recommendation and finding.recommendation not in category_scores[category]["recommendations"]:
                category_scores[category]["recommendations"].append(finding.recommendation)
        
        # Convert to SecurityScore objects
        result = {}
        for category, data in category_scores.items():
            result[category] = SecurityScore(
                score=round(data["score"], 1),
                findings=data["findings"],
                recommendations=data["recommendations"]
            )
            
        return result

    def _prioritize_actions(self, findings: List[VulnerabilityFinding]) -> List[str]:
        """Generate priority actions based on findings"""
        priority_actions = []
        
        # Sort findings by severity and confidence
        sorted_findings = sorted(
            findings,
            key=lambda f: (
                RiskLevel.CRITICAL == f.severity,
                RiskLevel.HIGH == f.severity,
                RiskLevel.MEDIUM == f.severity,
                f.confidence
            ),
            reverse=True
        )
        
        # Generate actions from the findings
        for finding in sorted_findings:
            action = f"[{finding.severity}] {finding.title}: {finding.recommendation[:100]}..."
            priority_actions.append(action)
            
            # Limit to 10 actions
            if len(priority_actions) >= 10:
                break
                
        return priority_actions

    async def initialize(self):
        """Initialize services"""
        try:
            # Initialize the finding validator
            await self.finding_validator.initialize()
            
            logger.info("Security assessment service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing security assessment service: {str(e)}")
            raise

    async def store_assessment_result(self, result: SecurityAssessmentResult, db: Session, vector_store: VectorStore = None) -> None:
        """Store assessment result in the database and vector store"""
        try:
            # Store in relational database
            assessment_crud = AssessmentCRUD(db)
            db_result = await assessment_crud.create_assessment(result)
            
            # Store vulnerabilities in vector database if available
            if vector_store:
                await self._store_vulnerabilities_in_vector_db(vector_store, result.vulnerabilities)
                
            logger.info(f"Stored assessment result with ID: {db_result.id}")
            
        except Exception as e:
            logger.error(f"Error storing assessment result: {str(e)}")
            raise

    async def _store_vulnerabilities_in_vector_db(self, vector_store: VectorStore, vulnerabilities: List[VulnerabilityFinding]) -> None:
        """Store vulnerabilities in vector database for similarity search"""
        try:
            embeddings_service = EmbeddingsService()
            
            for vuln in vulnerabilities:
                # Create text for embedding
                text = f"{vuln.title}. {vuln.description}"
                
                # Generate embedding
                embedding = await embeddings_service.generate_embedding(text)
                
                # Store in vector database
                await vector_store.store_embedding(
                    text=text,
                    embedding=embedding,
                    metadata={
                        "id": vuln.id,
                        "title": vuln.title,
                        "severity": vuln.severity,
                        "category": vuln.category,
                        "confidence": vuln.confidence
                    }
                )
                
            logger.info(f"Stored {len(vulnerabilities)} vulnerabilities in vector database")
            
        except Exception as e:
            logger.error(f"Error storing vulnerabilities in vector database: {str(e)}")
            logger.error(f"Will continue without vector storage: {str(e)}")
            # Don't re-raise the exception to allow the process to continue 