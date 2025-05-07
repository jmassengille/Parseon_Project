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

class FindingValidator:
    """
    Validates findings from security analysis against known patterns
    to reduce hallucination and increase confidence.
    """
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """Initialize with optional knowledge base"""
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.embeddings_service = EmbeddingsService()
        
        # Thresholds for validation
        self.similarity_threshold = 0.5  # Minimum similarity score to validate
        self.boost_threshold = 0.7     # Similarity score to boost confidence
        
        # Initialize embedding cache
        self._vulnerability_embeddings = {}
    
    async def initialize(self):
        """Initialize embeddings and services"""
        await self.embeddings_service.initialize()
        
        # Pre-compute embeddings for known vulnerability types
        if not self._vulnerability_embeddings:
            await self._initialize_vulnerability_embeddings()
    
    async def _initialize_vulnerability_embeddings(self):
        """Initialize embeddings for known vulnerability types"""
        vulnerability_types = [
            # Prompt injection
            "Prompt injection vulnerability where user input is directly used in prompts",
            "System prompt leak vulnerability",
            "Indirect prompt injection through database stored content",
            
            # API security
            "Missing rate limiting on AI API calls",
            "Hardcoded API keys in source code",
            "Insufficient API key rotation",
            
            # Configuration
            "Overly permissive AI model temperature setting",
            "Missing token budget controls",
            "Excessive max tokens configuration",
            
            # Error handling
            "AI-specific error types not handled properly",
            "Error messages revealing prompt details"
        ]
        
        # Compute embeddings for each vulnerability type
        for vuln_type in vulnerability_types:
            embedding = await self.embeddings_service.generate_embedding(vuln_type)
            self._vulnerability_embeddings[vuln_type] = embedding
    
    async def validate_findings(self, findings: List[VulnerabilityFinding]) -> List[VulnerabilityFinding]:
        """
        Validate findings against known patterns using embeddings
        Returns the findings with updated confidence scores and validation info
        """
        if not findings:
            return []
        
        # Make sure embeddings are initialized
        if not self._vulnerability_embeddings:
            await self._initialize_vulnerability_embeddings()
        
        validated_findings = []
        
        for finding in findings:
            # Get embedding for the finding description
            description = f"{finding.title}. {finding.description[:300]}"
            finding_embedding = await self.embeddings_service.generate_embedding(description)
            
            # Find the most similar known vulnerability
            best_similarity = 0
            most_similar_vuln = None
            
            for vuln_type, vuln_embedding in self._vulnerability_embeddings.items():
                similarity = self._calculate_similarity(finding_embedding, vuln_embedding)
                if similarity > best_similarity:
                    best_similarity = similarity
                    most_similar_vuln = vuln_type
            
            # Update finding based on similarity score
            validated_finding = self._update_finding_confidence(finding, best_similarity, most_similar_vuln)
            validated_findings.append(validated_finding)
            
            print(f"Validation: '{finding.title}' -> Similarity: {best_similarity:.2f}, Similar to: {most_similar_vuln}")
        
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