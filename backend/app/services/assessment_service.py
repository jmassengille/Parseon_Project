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
from app.services.embeddings_service import EmbeddingsService
from app.services.vector_store import VectorStore
import asyncio

logger = logging.getLogger(__name__)

# Global services for singleton pattern to avoid repeated initialization
_embedding_service = None
_base_analyzer = None
_finding_validator = None

# Configurable timeout settings with reasonable defaults
ANALYSIS_TIMEOUT = int(os.getenv("ASSESSMENT_TIMEOUT_SECONDS", "60"))  # Default 60 seconds for total assessment
VALIDATION_TIMEOUT = int(os.getenv("VALIDATION_TIMEOUT_SECONDS", "10"))  # Default 10 seconds for validation
API_CALL_TIMEOUT = int(os.getenv("API_CALL_TIMEOUT_SECONDS", "30"))  # Default 30 seconds for API call

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
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=API_CALL_TIMEOUT  # Use configurable timeout
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        
        # Risk weights for score calculation
        self.risk_weights = {
            RiskLevel.CRITICAL: 15.0,  # Increased from 1.0
            RiskLevel.HIGH: 12.0,      # Increased from 6.0
            RiskLevel.MEDIUM: 3.0,     # Increased from 0.7
            RiskLevel.LOW: 1.0         # Increased from 0.3
        }
        
        # Category weights for overall score
        self.category_weights = {
            SecurityCategory.API_SECURITY: 0.35,
            SecurityCategory.PROMPT_SECURITY: 0.35,
            SecurityCategory.CONFIGURATION: 0.15,
            SecurityCategory.ERROR_HANDLING: 0.15
        }
        
        # Store initialized flag for lazy initialization
        self.initialized = False
    
    async def _ensure_initialized(self):
        """Lazily initialize services only when needed"""
        global _embedding_service, _base_analyzer, _finding_validator
        
        if not self.initialized:
            # Use global services if available, otherwise create them
            if _base_analyzer is None:
                _base_analyzer = BaseModelAnalyzer()
            self.base_analyzer = _base_analyzer
            
            # Initialize finding validator with knowledge base (if needed)
            if _finding_validator is None:
                # Skip KB initialization to improve speed
                empty_kb = KnowledgeBase()
                _finding_validator = FindingValidator(knowledge_base=empty_kb)
                
                # Initialize embedding service (only once)
                if _embedding_service is None:
                    _embedding_service = EmbeddingsService()
                    await _embedding_service.initialize()
                
                # Initialize validator with existing embedding service
                await _finding_validator.initialize()
            
            self.finding_validator = _finding_validator
            self.initialized = True

    def _set_category_weights_for_mode(self, scan_mode: Optional[ScanMode]):
        """Adjust category weights based on scan mode"""
        if scan_mode == ScanMode.API_SECURITY:
            self.category_weights = {
                SecurityCategory.API_SECURITY: 0.60,
                SecurityCategory.PROMPT_SECURITY: 0.20,
                SecurityCategory.CONFIGURATION: 0.10,
                SecurityCategory.ERROR_HANDLING: 0.10
            }
        elif scan_mode == ScanMode.PROMPT_SECURITY:
            self.category_weights = {
                SecurityCategory.API_SECURITY: 0.20,
                SecurityCategory.PROMPT_SECURITY: 0.60,
                SecurityCategory.CONFIGURATION: 0.10,
                SecurityCategory.ERROR_HANDLING: 0.10
            }

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
        start_time = datetime.now()
        
        try:
            # Set a reasonable timeout for this analysis
            analysis_timeout = ANALYSIS_TIMEOUT  # Use configurable timeout
            
            # Log assessment start
            logger.info(f"Starting assessment for {assessment_input.organization_name}/{assessment_input.project_name}")
            
            # Lazy initialization of services to improve startup time
            await self._ensure_initialized()
            
            # Validate input
            self._validate_input(assessment_input)
            
            # Set category weights based on scan mode
            self._set_category_weights_for_mode(assessment_input.scan_mode)
            
            # Initialize findings lists
            all_findings = []
            
            # Create tasks for parallel processing
            tasks = []
            
            # Process implementation details (API/code)
            code_count = 0
            if assessment_input.implementation_details:
                for component, code in assessment_input.implementation_details.items():
                    # Skip empty code
                    if not code or len(code.strip()) < 10:
                        continue
                        
                    # Skip if code is too large (over 30KB)
                    if len(code) > 30000:
                        logger.warning(f"Skipping {component} as it exceeds size limit (size: {len(code)})")
                        continue
                    
                    # Limit the number of code components to analyze to prevent memory issues on Railway
                    code_count += 1
                    if code_count > 5:  # Only analyze up to 5 code components
                        logger.warning(f"Skipping remaining code components after {code_count-1} to conserve memory")
                        break
                    
                    # Add task for code analysis
                    task = self.base_analyzer.analyze_code(code, component)
                    tasks.append(task)
            
            # Process configs
            config_count = 0
            if assessment_input.configs:
                for config_type, content in assessment_input.configs.items():
                    # Skip empty configs
                    if not content or len(content.strip()) < 10:
                        continue
                    
                    # Skip if content is too large
                    if len(content) > 30000:
                        logger.warning(f"Skipping config {config_type} as it exceeds size limit (size: {len(content)})")
                        continue
                    
                    # Limit the number of config files to analyze
                    config_count += 1
                    if config_count > 3:  # Only analyze up to 3 config files
                        logger.warning(f"Skipping remaining config files after {config_count-1} to conserve memory")
                        break
                    
                    # Add task for config analysis
                    task = self.base_analyzer.analyze_config(content)
                    tasks.append(task)
            
            # Run all analysis tasks in parallel with a timeout
            if tasks:
                try:
                    # Use asyncio.wait_for to set a global timeout for all tasks
                    findings_lists = await asyncio.wait_for(
                        asyncio.gather(*tasks),
                        timeout=analysis_timeout
                    )
                    
                    # Combine all findings
                    for findings in findings_lists:
                        all_findings.extend(findings)
                except asyncio.TimeoutError:
                    logger.warning(f"Analysis timed out after {analysis_timeout} seconds. Proceeding with partial results.")
                    # Try to get any completed results
                    for task in tasks:
                        if task.done() and not task.exception():
                            try:
                                findings = task.result()
                                all_findings.extend(findings)
                            except Exception as e:
                                logger.error(f"Error getting task result: {str(e)}")
                except MemoryError:
                    logger.error("Memory limit exceeded during analysis. Proceeding with partial results.")
                    # Try to get any completed results
                    for task in tasks:
                        if task.done() and not task.exception():
                            try:
                                findings = task.result()
                                all_findings.extend(findings)
                            except Exception as e:
                                logger.error(f"Error getting task result: {str(e)}")
            
            # Deduplicate findings based on title
            all_findings = self._deduplicate_findings(all_findings)
            
            # Only validate findings if we have at least one
            # And limit to 20 max findings to validate to save time
            if all_findings:
                # Sort by severity first
                severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
                all_findings = sorted(
                    all_findings,
                    key=lambda f: severity_order.get(f.severity.upper(), 4)
                )
                
                # Take at most 20 findings to validate (prioritizing by severity)
                findings_to_validate = all_findings[:20]
                if len(findings_to_validate) < len(all_findings):
                    logger.info(f"Limiting validation to {len(findings_to_validate)} out of {len(all_findings)} findings")
                
                # Use fast_mode if more than 10 findings to validate or if we've already spent a lot of time
                use_fast_mode = len(findings_to_validate) > 10
                try:
                    validated_findings = await asyncio.wait_for(
                        self.finding_validator.validate_findings(findings_to_validate, fast_mode=use_fast_mode),
                        timeout=VALIDATION_TIMEOUT  # Use configurable timeout
                    )
                    
                    # Replace the findings we validated
                    for i, finding in enumerate(validated_findings):
                        all_findings[i] = finding
                except asyncio.TimeoutError:
                    logger.warning(f"Validation timed out after {VALIDATION_TIMEOUT} seconds. Proceeding with unvalidated findings.")
                except Exception as e:
                    logger.error(f"Error during validation: {str(e)}. Proceeding with unvalidated findings.")
            
            # Filter out false-positive API key findings for env var references
            def is_env_var_api_key_finding(finding):
                if "api key" in finding.title.lower() and (
                    any("OPENAI_API_KEY" in s for s in getattr(finding, 'code_snippets', [])) or
                    "OPENAI_API_KEY" in finding.description
                ):
                    return True
                return False
            all_findings = [f for f in all_findings if not is_env_var_api_key_finding(f)]
            
            # Update token usage BEFORE creating the result
            self.token_usage["prompt_tokens"] += self.base_analyzer.token_usage["prompt_tokens"]
            self.token_usage["completion_tokens"] += self.base_analyzer.token_usage["completion_tokens"]
            
            # Calculate category scores first
            category_scores = self._calculate_category_scores(all_findings)
            
            # Then calculate overall score based on weighted category scores
            overall_score = self._calculate_weighted_score(category_scores)
            
            # Calculate risk level based on the overall score
            risk_level = self._calculate_risk_level(overall_score)

            # Create the assessment result
            assessment_result = SecurityAssessmentResult(
                organization_name=assessment_input.organization_name,
                project_name=assessment_input.project_name,
                timestamp=datetime.now(),
                overall_score=overall_score,
                overall_risk_level=risk_level,
                vulnerabilities=all_findings,
                category_scores=category_scores,
                priority_actions=self._prioritize_actions(all_findings),
                ai_model_used=self.model,
                token_usage=self.token_usage
            )
            
            # Calculate processing time
            end_time = datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"Assessment completed for {assessment_input.organization_name}/{assessment_input.project_name} in {duration_seconds:.1f} seconds")
            logger.info(f"Assessment result: score={assessment_result.overall_score}, risk level={assessment_result.overall_risk_level}")
            logger.info(f"Found {len(all_findings)} vulnerabilities across {len(assessment_result.category_scores)} categories")
            
            logger.debug(f"Token usage: {self.token_usage['prompt_tokens']} prompt, {self.token_usage['completion_tokens']} completion")
            
            # Return the assessment result
            return assessment_result
            
        except Exception as e:
            # Calculate processing time even for failures
            end_time = datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()
            
            logger.error(f"Error in security assessment after {duration_seconds:.1f} seconds: {str(e)}")
            logger.error(f"Stack trace:", exc_info=True)
            
            # If it's a Railway deployment limitation, provide a more specific error
            if "ConnectionResetError" in str(e) or "ConnectTimeout" in str(e):
                raise AssessmentError(
                    message="Connection error while performing assessment. This may be due to server load or network issues.",
                    status_code=503
                )
            # If it's a memory limit issue
            elif "MemoryError" in str(e) or "ResourceExhaustedError" in str(e):
                raise AssessmentError(
                    message="Memory limit exceeded during assessment. Please try again with a smaller input or fewer components.",
                    status_code=413
                )
            # If it's a timeout
            elif "TimeoutError" in str(e) or "asyncio.exceptions.TimeoutError" in str(e):
                raise AssessmentError(
                    message="Assessment timed out. Please try again with a smaller input or fewer components.",
                    status_code=504
                )
            # Re-raise the original exception
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

    def _calculate_overall_score(self, findings: List[VulnerabilityFinding]) -> float:
        """Calculate overall security score based on findings"""
        if not findings:
            return 95.0  # No findings = excellent score
            
        base_score = 100.0
        
        # Calculate penalty for each finding based on severity
        for finding in findings:
            # Get the risk weight for this severity
            risk_weight = self.risk_weights.get(finding.severity, 0.5)
            
            # Calculate penalty - adjusted by confidence
            penalty = risk_weight * finding.confidence * 3.0
            
            # Apply penalty
            base_score -= penalty
            
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, base_score))

    def _calculate_weighted_score(self, category_scores: Dict[SecurityCategory, SecurityScore]) -> float:
        """Calculate overall score based on weighted category scores"""
        if not category_scores:
            return 95.0  # No categories = excellent score
            
        total_weight = 0.0
        weighted_sum = 0.0
        
        # Calculate weighted sum of category scores
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 0.0)
            total_weight += weight
            weighted_sum += score.score * weight
        
        # If no weights, return simple average
        if total_weight == 0:
            return sum(score.score for score in category_scores.values()) / len(category_scores)
            
        # Calculate weighted average
        weighted_average = weighted_sum / total_weight
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, weighted_average))

    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Calculate overall risk level based on score"""
        if score >= 85:
            return RiskLevel.LOW
        elif score >= 65:
            return RiskLevel.MEDIUM
        elif score >= 35:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _calculate_category_scores(self, findings: List[VulnerabilityFinding]) -> Dict[SecurityCategory, SecurityScore]:
        """Calculate scores for each security category"""
        category_scores = {}
        
        # Initialize scores for all categories
        for category in SecurityCategory:
            category_scores[category] = SecurityScore(
                category=category,
                score=100.0,
                weight=self.category_weights.get(category, 0.0)
            )
            
        # Track issues found separately
        issues_count = {category: 0 for category in SecurityCategory}
        
        # Process each finding
        for finding in findings:
            category = finding.category
            
            # Skip if category not recognized
            if category not in category_scores:
                continue
                
            # Get the score for this category
            score = category_scores[category]
            
            # Get the risk weight for this severity
            risk_weight = self.risk_weights.get(finding.severity, 0.5)
            
            # Calculate penalty - adjusted by confidence
            penalty = risk_weight * finding.confidence * 4.0  # Higher than overall score multiplier
            
            # Increment issues found in our tracking dictionary
            issues_count[category] += 1
            
            # Apply penalty
            score.score = max(0.0, score.score - penalty)
            
            # Add findings to the score object
            if issues_count[category] <= 5:  # Limit to 5 findings per category
                score.findings.append(finding.title)
        
        return category_scores

    def _prioritize_actions(self, findings: List[VulnerabilityFinding]) -> List[str]:
        """Create prioritized action items from findings"""
        if not findings:
            return []
            
        # Sort findings by severity and confidence
        sorted_findings = sorted(
            findings, 
            key=lambda f: (
                0 if f.severity == RiskLevel.CRITICAL else
                1 if f.severity == RiskLevel.HIGH else
                2 if f.severity == RiskLevel.MEDIUM else 3,
                -f.confidence
            )
        )
        
        # Create priority actions (limit to top 5)
        priority_actions = []
        for i, finding in enumerate(sorted_findings[:5]):
            # Format as a string instead of dictionary
            action_string = f"[{finding.severity}] {finding.title}: {finding.recommendation}"
            priority_actions.append(action_string)
            
        return priority_actions
    
    def _deduplicate_findings(self, findings: List[VulnerabilityFinding]) -> List[VulnerabilityFinding]:
        """Remove duplicate findings based on title/description similarity"""
        if not findings or len(findings) <= 1:
            return findings
            
        # Use a set to track unique finding titles
        unique_titles = set()
        unique_findings = []
        
        for finding in findings:
            # Create a normalized version of the title
            normalized_title = re.sub(r'\s+', ' ', finding.title.lower().strip())
            
            # Skip if we've seen this title before
            if normalized_title in unique_titles:
                continue
                
            # Add to unique findings and title set
            unique_titles.add(normalized_title)
            unique_findings.append(finding)
            
        return unique_findings

    async def initialize(self):
        """Initialize services"""
        try:
            # Call _ensure_initialized() instead of directly accessing finding_validator
            await self._ensure_initialized()
            logger.info("Security assessment service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing security assessment service: {str(e)}")
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