"""
Finding Validator for AI Security Findings

This module validates findings from the LLM against known patterns using 
embeddings and other validation strategies to reduce hallucinations and
increase confidence in the findings.
"""

from typing import Dict, List, Optional, Any
import logging
import numpy as np
from app.schemas.assessment import VulnerabilityFinding
from app.core.knowledge_base import KnowledgeBase
from app.services.embeddings_service import EmbeddingsService

logger = logging.getLogger(__name__)

# Global embedding cache to persist across requests
_GLOBAL_EMBEDDING_CACHE = {}
_MAX_CACHE_ENTRIES = 100  # Limit cache size to avoid memory issues

class FindingValidator:
    """
    Validates findings from security analysis against known patterns
    to reduce hallucination and increase confidence.
    """
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """Initialize with optional knowledge base"""
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.embeddings_service = EmbeddingsService()
        
        # Thresholds for validation - slightly lower for better performance
        self.similarity_threshold = 0.45  # Slightly lower than before
        self.boost_threshold = 0.65     # Slightly lower than before
        
        # Use global cache for embeddings
        self._vulnerability_embeddings = _GLOBAL_EMBEDDING_CACHE
    
    async def initialize(self):
        """Initialize embeddings and services"""
        await self.embeddings_service.initialize()
        
        # Pre-compute embeddings for known vulnerability types - only if not already cached
        if not self._vulnerability_embeddings:
            await self._initialize_vulnerability_embeddings()
    
    async def _initialize_vulnerability_embeddings(self):
        """Initialize embeddings for known vulnerability types"""
        # Reduced list of vulnerability types to improve performance
        vulnerability_types = [
            # Combined prompt injection vulnerabilities
            "Prompt injection vulnerability in AI systems",
            
            # Combined API security issues
            "Missing rate limiting and hardcoded API keys",
            
            # Combined configuration issues
            "Insecure AI model configuration settings",
            
            # Combined error handling issues
            "Poor error handling in AI systems"
        ]
        
        # Batch process embeddings for performance
        all_embeddings = await self.embeddings_service.generate_embeddings_batch(vulnerability_types)
        
        # Store in cache
        for i, vuln_type in enumerate(vulnerability_types):
            self._vulnerability_embeddings[vuln_type] = all_embeddings[i]
            
        # Prune cache if needed
        self._prune_cache()
    
    def _prune_cache(self):
        """Prune the embedding cache if it exceeds maximum size"""
        if len(self._vulnerability_embeddings) > _MAX_CACHE_ENTRIES:
            # Remove oldest entries (simple approximation by converting to list)
            excess_count = len(self._vulnerability_embeddings) - _MAX_CACHE_ENTRIES
            keys_to_remove = list(self._vulnerability_embeddings.keys())[:excess_count]
            for key in keys_to_remove:
                del self._vulnerability_embeddings[key]
    
    async def validate_findings(self, findings: List[VulnerabilityFinding], fast_mode: bool = False) -> List[VulnerabilityFinding]:
        """
        Validate findings against known patterns using embeddings
        Returns the findings with updated confidence scores and validation info
        
        Args:
            findings: List of vulnerability findings to validate
            fast_mode: If True, use keyword-based validation instead of embeddings for improved speed
        """
        if not findings:
            return []
        
        # Fast mode uses keyword matching instead of embeddings
        if fast_mode:
            return self._fast_validate_findings(findings)
        
        # Make sure embeddings are initialized
        if not self._vulnerability_embeddings:
            await self._initialize_vulnerability_embeddings()
        
        validated_findings = []
        
        # Prepare batch of descriptions for embedding generation
        descriptions = []
        for finding in findings:
            description = f"{finding.title}. {finding.description[:300]}"
            descriptions.append(description)
        
        # Generate embeddings in batch
        finding_embeddings = await self.embeddings_service.generate_embeddings_batch(descriptions)
        
        # Process each finding with its embedding
        for i, finding in enumerate(findings):
            # Find the most similar known vulnerability
            best_similarity = 0
            most_similar_vuln = None
            
            # Get the embedding for this finding
            finding_embedding = finding_embeddings[i]
            
            for vuln_type, vuln_embedding in self._vulnerability_embeddings.items():
                similarity = self._calculate_similarity(finding_embedding, vuln_embedding)
                if similarity > best_similarity:
                    best_similarity = similarity
                    most_similar_vuln = vuln_type
            
            # Update finding based on similarity score
            validated_finding = self._update_finding_confidence(finding, best_similarity, most_similar_vuln)
            validated_findings.append(validated_finding)
            
            # Avoid costly print statement in tight loop
            logger.debug(f"Validation: '{finding.title}' -> Similarity: {best_similarity:.2f}, Similar to: {most_similar_vuln}")
        
        return validated_findings
    
    def _fast_validate_findings(self, findings: List[VulnerabilityFinding]) -> List[VulnerabilityFinding]:
        """Fast validation using keyword matching instead of embeddings"""
        validated_findings = []
        
        # Keywords for different vulnerability categories
        keywords = {
            "PROMPT_SECURITY": ["prompt injection", "system prompt", "prompt", "user input", "sanitization"],
            "API_SECURITY": ["api key", "rate limit", "authentication", "authorization", "token"],
            "CONFIGURATION": ["configuration", "parameter", "temperature", "max_tokens", "model settings"],
            "ERROR_HANDLING": ["error handling", "exception", "validation", "error message"]
        }
        
        for finding in findings:
            # Calculate keyword matches
            category = finding.category
            title_lower = finding.title.lower()
            description_lower = finding.description.lower()
            
            # Default confidence
            confidence = finding.confidence
            
            # Adjust confidence based on keyword matches
            if category in keywords:
                category_keywords = keywords[category]
                match_count = sum(1 for keyword in category_keywords if 
                                  keyword in title_lower or keyword in description_lower)
                
                # Set validation info
                validation_info = {
                    "validation_score": min(1.0, match_count / len(category_keywords)),
                    "similar_vulnerability": category,
                    "validated": match_count > 0,
                    "confidence_adjustment": "keyword_based"
                }
                
                # Adjust confidence based on keyword matches
                if match_count >= 2:
                    confidence = min(1.0, confidence + 0.1)
                    validation_info["confidence_adjustment"] = "boosted"
                elif match_count == 0:
                    confidence = max(0.4, confidence - 0.1)
                    validation_info["confidence_adjustment"] = "reduced"
            else:
                # For unknown categories, use a default validation
                validation_info = {
                    "validation_score": 0.5,
                    "similar_vulnerability": "Unknown",
                    "validated": True,
                    "confidence_adjustment": "unchanged"
                }
                
            # Create validated finding
            updated_finding = VulnerabilityFinding(
                id=finding.id,
                title=finding.title,
                description=finding.description,
                severity=finding.severity,
                category=finding.category,
                code_snippets=finding.code_snippets,
                recommendation=finding.recommendation,
                confidence=confidence,
                validation_info=validation_info
            )
            
            validated_findings.append(updated_finding)
            
        return validated_findings
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0
        
        # Convert to numpy arrays
        v1 = np.array(embedding1)
        v2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
            
        return dot_product / (norm1 * norm2)
    
    def _update_finding_confidence(
        self, 
        finding: VulnerabilityFinding, 
        similarity: float, 
        similar_vuln: Optional[str]
    ) -> VulnerabilityFinding:
        """Update finding confidence based on validation results"""
        # Create a copy of the finding to avoid modifying the original
        updated_finding = VulnerabilityFinding(
            id=finding.id,
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            category=finding.category,
            code_snippets=finding.code_snippets,
            recommendation=finding.recommendation,
            confidence=finding.confidence
        )
        
        # Create validation info
        validation_info = {
            "validation_score": similarity,
            "similar_vulnerability": similar_vuln,
            "validated": bool(similarity >= self.similarity_threshold)
        }
        
        # Adjust confidence based on similarity
        if similarity >= self.boost_threshold:
            # High similarity - boost confidence
            updated_finding.confidence = min(1.0, finding.confidence + 0.15)
            validation_info["confidence_adjustment"] = "boosted"
        elif similarity < self.similarity_threshold:
            # Low similarity - reduce confidence
            updated_finding.confidence = max(0.1, finding.confidence - 0.2)
            validation_info["confidence_adjustment"] = "reduced"
        else:
            # Medium similarity - no change
            validation_info["confidence_adjustment"] = "unchanged"
        
        # Set the validation info on the finding
        updated_finding.validation_info = validation_info
        
        return updated_finding
    
    async def keyword_validation(self, finding: VulnerabilityFinding) -> Dict[str, Any]:
        """
        Alternate validation method using keyword matching
        This can be used as a fallback or in addition to embedding validation
        """
        # Placeholder for keyword validation logic
        # This would check for specific keywords related to known vulnerabilities
        return {
            "keyword_validation": "not_implemented",
            "score": 0.5
        } 