from typing import Dict, List, Optional
from pydantic import BaseModel
import json
import csv
import aiohttp
import asyncio
from pathlib import Path
import logging
import os
import tempfile
import zipfile
import re
import xmltodict
from slugify import slugify
import yaml

logger = logging.getLogger(__name__)

class SecurityPattern(BaseModel):
    """Represents a security pattern or rule in the knowledge base."""
    id: str
    category: str
    description: str
    severity: str = "MEDIUM"  # Default severity
    examples: List[str] = []  # Default empty examples list
    mitigation: str = "See source documentation for mitigation strategies"  # Default mitigation message
    references: List[str] = []  # Default empty references list
    source: str  # Added to track the source of the pattern
    semantic_indicators: List[str] = []  # Keywords and phrases that indicate this pattern
    context_rules: List[str] = []  # Context-specific rules for pattern validation
    related_patterns: List[str] = []  # IDs of semantically related patterns

class KnowledgeBase:
    """Manages the security knowledge base for grounding AI assessments."""
    
    def __init__(self, patterns_file: Optional[str] = None, test_mode: bool = False):
        self.patterns: Dict[str, SecurityPattern] = {}
        self.patterns_file = patterns_file or str(Path(__file__).parent / "data" / "security_patterns.json")
        self.test_mode = True  # Force test mode
        self.semantic_clusters: Dict[str, List[str]] = {}  # Category -> List of pattern IDs
        
        # Always use test data for now
        self.sources = {
            "owasp_ai": str(Path(__file__).parent / "test_data" / "security_patterns.md"),
            "mitre_atlas": str(Path(__file__).parent / "test_data" / "techniques.md"),
            "mitre_matrix": str(Path(__file__).parent / "test_data" / "atlas.yaml")
        }
        # Commented out external sources until they're available
        # if test_mode:
        #     self.sources = {
        #         "owasp_ai": str(Path(__file__).parent / "test_data" / "security_patterns.md"),
        #         "mitre_atlas": str(Path(__file__).parent / "test_data" / "techniques.md"),
        #         "mitre_matrix": str(Path(__file__).parent / "test_data" / "atlas.yaml")
        #     }
        # else:
        #     self.sources = {
        #         "owasp_ai": "https://raw.githubusercontent.com/OWASP/www-project-ai-security-and-privacy-guide/main/content/ai_exchange/docs/security_patterns.md",
        #         "mitre_atlas": "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques/T0001.md",
        #         "mitre_matrix": "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml"
        #     }
    
    async def initialize(self):
        """Initialize the knowledge base by loading patterns from external sources."""
        try:
            # Load local patterns first
            self._load_patterns()
            
            # Create data directory if it doesn't exist
            Path(self.patterns_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Load patterns from external sources and merge with local patterns
            await self._load_external_patterns()
            
            # Save combined patterns to local file
            self._save_patterns()
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            # Ensure we at least have local patterns if external sources fail
            self._load_patterns()
    
    async def _load_external_patterns(self):
        """Load security patterns from external sources."""
        if self.test_mode:
            for source_name, path in self.sources.items():
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if path.endswith('.md'):
                            patterns = self._extract_patterns_from_markdown(content, source_name)
                            self.patterns.update(patterns)
                        elif path.endswith('.yaml') or path.endswith('.yml'):
                            patterns = self._extract_patterns_from_yaml(content, source_name)
                            self.patterns.update(patterns)
                except Exception as e:
                    logger.error(f"Error loading patterns from {source_name}: {str(e)}")
            return

        async with aiohttp.ClientSession() as session:
            for source_name, url in self.sources.items():
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            if url.endswith('.md'):
                                patterns = self._extract_patterns_from_markdown(content, source_name)
                                self.patterns.update(patterns)
                            elif url.endswith('.yaml') or url.endswith('.yml'):
                                patterns = self._extract_patterns_from_yaml(content, source_name)
                                self.patterns.update(patterns)
                            else:
                                logger.warning(f"Unsupported file format for {source_name}: {url}")
                        else:
                            logger.warning(f"Failed to load patterns from {source_name}: {response.status}")
                except Exception as e:
                    logger.error(f"Error loading patterns from {source_name}: {str(e)}")
    
    def _extract_patterns_from_markdown(self, content: str, source_name: str) -> Dict[str, SecurityPattern]:
        """Extract security patterns from markdown content with semantic understanding."""
        patterns = {}
        
        # Split content into sections
        sections = content.split('\n## ')
        
        for section in sections:
            if not section.strip():
                continue
                
            # Extract title and description
            lines = section.split('\n')
            title = lines[0].strip('# ')
            
            # Extract description with context awareness
            description_lines = []
            context_lines = []
            for line in lines[1:]:
                if line.strip():
                    if len(description_lines) < 3:  # First 3 non-empty lines are description
                        description_lines.append(line.strip())
                    else:
                        context_lines.append(line.strip())
                elif description_lines:  # Stop at first empty line after content
                    break
            description = ' '.join(description_lines)
            
            # Extract examples with context
            examples = []
            code_blocks = re.findall(r'```[^\n]*\n(.*?)```', section, re.DOTALL)
            for block in code_blocks:
                # Include some context around the code block
                block_lines = block.strip().split('\n')
                if len(block_lines) > 1:
                    examples.append({
                        'code': block.strip(),
                        'context': self._extract_context_around_block(section, block)
                    })
            
            # Extract semantic indicators
            semantic_indicators = self._extract_semantic_indicators(section, title, description)
            
            # Extract context rules
            context_rules = self._extract_context_rules(section, semantic_indicators)
            
            # Create pattern ID
            pattern_id = f"{source_name}_{slugify(title)}"
            
            # Create security pattern
            pattern = SecurityPattern(
                id=pattern_id,
                category=self._determine_category(title, description),
                description=description,
                severity=self._determine_severity(section),
                examples=[ex['code'] for ex in examples],  # Keep backward compatibility
                mitigation=self._extract_mitigation(section, context_lines),
                references=self._extract_references(section),
                source=source_name,
                semantic_indicators=semantic_indicators,
                context_rules=context_rules,
                related_patterns=[]  # Will be populated after all patterns are loaded
            )
            
            patterns[pattern_id] = pattern
            
        return patterns
    
    def _extract_patterns_from_yaml(self, content: str, source_name: str) -> Dict[str, SecurityPattern]:
        """Extract security patterns from YAML content."""
        patterns = {}
        try:
            data = yaml.safe_load(content)
            
            # Handle MITRE ATLAS format
            if source_name == "mitre_matrix" and "matrices" in data:
                matrix = data["matrices"][0]  # Get first matrix
                
                # Process techniques as patterns
                for technique in matrix.get("techniques", []):
                    pattern_id = f"{source_name}_{technique['id']}"
                    
                    # Extract examples from procedure examples
                    examples = []
                    for procedure in technique.get("procedures", []):
                        if "example" in procedure:
                            examples.append(procedure["example"])
                    
                    # Create security pattern
                    pattern = SecurityPattern(
                        id=pattern_id,
                        category=technique.get("tactic", "General Security"),
                        description=technique.get("description", ""),
                        severity=self._determine_severity_from_impact(technique.get("impact", [])),
                        pattern=technique.get("detection", ""),
                        examples=examples,
                        mitigation=technique.get("mitigation", "See MITRE ATLAS documentation"),
                        references=technique.get("references", []),
                        source=source_name
                    )
                    
                    patterns[pattern_id] = pattern
                    
        except Exception as e:
            logger.error(f"Error parsing YAML content from {source_name}: {str(e)}")
            
        return patterns
        
    def _determine_severity_from_impact(self, impacts: List[str]) -> str:
        """Determine severity based on MITRE ATLAS impact levels."""
        if not impacts:
            return "medium"
            
        # Map impact keywords to severity levels
        severity_map = {
            "critical": ["catastrophic", "severe", "critical"],
            "high": ["significant", "major", "high"],
            "low": ["minor", "low", "limited"]
        }
        
        for impact in impacts:
            impact_lower = impact.lower()
            for severity, keywords in severity_map.items():
                if any(keyword in impact_lower for keyword in keywords):
                    return severity
                    
        return "medium"
    
    def _determine_severity(self, content: str) -> str:
        """Determine severity based on content analysis."""
        content_lower = content.lower()
        
        # Check for explicit severity indicators
        if re.search(r'severity:\s*(critical|high)', content_lower) or \
           re.search(r'(critical|high)\s*risk', content_lower) or \
           any(word in content_lower for word in ['devastating', 'severe', 'critical', 'dangerous']):
            return "critical"
        elif re.search(r'severity:\s*medium', content_lower) or \
             re.search(r'medium\s*risk', content_lower):
            return "medium"
        elif re.search(r'severity:\s*low', content_lower) or \
             re.search(r'low\s*risk', content_lower):
            return "low"
            
        # Default to medium if no clear indicators
        return "medium"
        
    def _extract_pattern(self, content: str) -> str:
        """Extract pattern or detection rules from content."""
        # Try to find explicit pattern sections
        pattern_match = re.search(r'(?i)(pattern|detection|rule):\s*(.*?)(?=\n\n|\Z)', content, re.DOTALL)
        if pattern_match:
            return pattern_match.group(2).strip()
            
        # If no explicit pattern, try to extract from code blocks
        code_blocks = re.findall(r'```[^\n]*\n(.*?)```', content, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
            
        return ""
    
    def _determine_category(self, title: str, description: str) -> str:
        """Determine pattern category using semantic analysis."""
        text = f"{title} {description}".lower()
        
        # Define category indicators with weights
        category_indicators = {
            "Model Security": {
                "terms": ["model", "training", "inference", "weights", "parameters", "neural", "ai system"],
                "weight": 1.5
            },
            "Data Security": {
                "terms": ["data", "dataset", "input", "output", "preprocessing", "validation"],
                "weight": 1.3
            },
            "API Security": {
                "terms": ["api", "endpoint", "request", "response", "http", "rest"],
                "weight": 1.2
            },
            "Prompt Security": {
                "terms": ["prompt", "instruction", "completion", "token", "generation"],
                "weight": 1.4
            }
        }
        
        # Calculate category scores
        category_scores = {}
        for category, indicators in category_indicators.items():
            score = sum(
                indicators["weight"] * text.count(term)
                for term in indicators["terms"]
            )
            category_scores[category] = score
        
        # Return category with highest score, or General Security if no strong match
        max_score = max(category_scores.values())
        if max_score > 0:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return "General Security"
    
    def _load_patterns(self) -> None:
        """Load security patterns from the JSON file."""
        try:
            if not Path(self.patterns_file).exists():
                logger.warning("Patterns file not found, initializing with empty patterns")
                self.patterns = {}
                return
                
            with open(self.patterns_file, 'r') as f:
                patterns_data = json.load(f)
                for pattern_data in patterns_data:
                    pattern = SecurityPattern(**pattern_data)
                    self.patterns[pattern.id] = pattern
        except Exception as e:
            logger.error(f"Error loading patterns from file: {str(e)}")
            self.patterns = {}
    
    def _save_patterns(self) -> None:
        """Save all patterns to the JSON file."""
        # Create data directory if it doesn't exist
        data_dir = Path(self.patterns_file).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Use model_dump instead of dict for Pydantic v2 compatibility
        patterns_data = [p.model_dump() for p in self.patterns.values()]
        with open(self.patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)
    
    def get_pattern(self, pattern_id: str) -> Optional[SecurityPattern]:
        """Retrieve a specific security pattern by ID."""
        return self.patterns.get(pattern_id)
    
    def get_patterns_by_category(self, category: str) -> List[SecurityPattern]:
        """Retrieve all patterns in a specific category."""
        return [p for p in self.patterns.values() if p.category == category]
    
    def get_patterns_by_source(self, source: str) -> List[SecurityPattern]:
        """Retrieve all patterns from a specific source."""
        return [p for p in self.patterns.values() if p.source == source]
    
    async def refresh_patterns(self):
        """Refresh patterns from external sources."""
        await self.initialize()

    def add_pattern(self, pattern: SecurityPattern) -> None:
        """Add a new security pattern to the knowledge base."""
        self.patterns[pattern.id] = pattern
        self._save_patterns()
    
    def _save_patterns(self) -> None:
        """Save all patterns to the JSON file."""
        patterns_data = [p.dict() for p in self.patterns.values()]
        with open(self.patterns_file, 'w') as f:
            json.dump(patterns_data, f, indent=2)

    def _extract_semantic_indicators(self, content: str, title: str, description: str) -> List[str]:
        """Extract semantic indicators from content."""
        indicators = set()
        
        # Add key terms from title and description
        for text in [title, description]:
            # Extract meaningful phrases (2-3 words)
            phrases = re.findall(r'\b\w+(?:\s+\w+){1,2}\b', text.lower())
            indicators.update(phrases)
            
            # Extract technical terms
            tech_terms = re.findall(r'\b[A-Za-z]+(?:[A-Z][a-z]*)*\b', text)
            indicators.update(term.lower() for term in tech_terms)
        
        # Extract domain-specific terminology
        security_terms = re.findall(
            r'\b(vulnerability|attack|exploit|security|risk|threat|protection|mitigation|defense)\b',
            content.lower()
        )
        indicators.update(security_terms)
        
        return list(indicators)

    def _extract_context_rules(self, content: str, semantic_indicators: List[str]) -> List[str]:
        """Extract context-specific rules based on content and semantic indicators."""
        rules = set()
        
        # Look for conditional statements and requirements
        requirement_patterns = [
            r'(?:must|should|needs? to|requires?|ensure)\s+([^.!?\n]+)',
            r'if\s+([^,\n]+),\s*then\s+([^.!?\n]+)',
            r'when\s+([^,\n]+),\s*([^.!?\n]+)',
            r'(?:verify|validate|check)\s+([^.!?\n]+)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                rule = match.group(1).strip()
                if any(indicator in rule.lower() for indicator in semantic_indicators):
                    rules.add(rule)
        
        return list(rules)

    def _extract_context_around_block(self, section: str, block: str) -> str:
        """Extract relevant context around a code block."""
        # Find the block's position in the section
        block_pos = section.find(block)
        if block_pos == -1:
            return ""
        
        # Get some context before and after the block
        context_start = max(0, block_pos - 200)
        context_end = min(len(section), block_pos + len(block) + 200)
        context = section[context_start:context_end]
        
        # Clean up the context
        context = re.sub(r'```[^`]+```', '', context)  # Remove other code blocks
        context = re.sub(r'\s+', ' ', context)  # Normalize whitespace
        
        return context.strip()

    def _extract_mitigation(self, section: str, context_lines: List[str]) -> str:
        """Extract mitigation strategies with context awareness."""
        mitigation = ""
        
        # Look for mitigation sections with various headers
        mitigation_headers = ['mitigation', 'remediation', 'solution', 'prevention', 'countermeasures']
        section_lower = section.lower()
        
        for header in mitigation_headers:
            pattern = r'(?i)' + re.escape(header) + r':\s*(.*?)(?=\n\n|\Z)'
            match = re.search(pattern, section, re.DOTALL)
            if match:
                mitigation = match.group(1).strip()
                break
        
        # If no explicit mitigation section found, try to extract from context
        if not mitigation and context_lines:
            mitigation_indicators = [
                'to prevent this',
                'can be mitigated',
                'should implement',
                'recommended to',
                'best practice'
            ]
            
            for line in context_lines:
                if any(indicator in line.lower() for indicator in mitigation_indicators):
                    mitigation = line.strip()
                    break
        
        return mitigation or "See source documentation for mitigation strategies"

    def _extract_references(self, section: str) -> List[str]:
        """Extract references from content."""
        references = []
        
        # Look for references in the section
        ref_section = re.search(r'(?i)(references|see also|related):\s*(.*?)(?=\n\n|\Z)', section, re.DOTALL)
        if ref_section:
            ref_lines = ref_section.group(2).strip().split('\n')
            references = [ref.strip('* ') for ref in ref_lines if ref.strip()]
        
        return references or [f"Source: {section.split('\n')[0].strip('# ')}"] 