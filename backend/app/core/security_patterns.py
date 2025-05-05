from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from .security_frameworks import SecurityFrameworkManager

class PatternCategory(str, Enum):
    CODE = "code"
    CONFIG = "config"
    MODEL = "model"
    PROMPT = "prompt"
    DATA = "data"
    INFRASTRUCTURE = "infrastructure"

class PatternSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class FrameworkMapping(BaseModel):
    """Mappings to security frameworks"""
    owasp_id: Optional[str] = None
    mitre_attack_id: Optional[str] = None
    cwe_id: Optional[str] = None
    nist_id: Optional[str] = None

class DetectionRule(BaseModel):
    pattern: str  # Regex or semantic pattern
    description: str
    confidence_modifier: float  # Affects final confidence score

class SecurityPattern(BaseModel):
    id: str
    title: str
    description: str
    category: PatternCategory
    severity: PatternSeverity
    detection_rules: List[DetectionRule]
    remediation_steps: List[str]
    false_positives: List[str]
    references: List[str]
    framework_mappings: FrameworkMapping
    examples: List[str] = []
    attack_scenarios: List[str] = []
    mitigation_guidelines: List[str] = []

class SecurityPatternsRepository:
    """Repository of critical security patterns for AI implementations"""
    
    def __init__(self):
        self.framework_manager = SecurityFrameworkManager()
        self.patterns: Dict[PatternCategory, List[SecurityPattern]] = {
            PatternCategory.PROMPT: [
                SecurityPattern(
                    id="PROMPT-INJ-001",
                    title="Direct Prompt Injection Vulnerability",
                    description="""
                    Critical Security Risk: Direct prompt injection vulnerability detected.
                    The application directly incorporates user input into AI prompts without proper sanitization
                    or boundary enforcement. This can lead to prompt injection attacks where malicious users
                    can override system instructions or extract sensitive information.
                    """,
                    category=PatternCategory.PROMPT,
                    severity=PatternSeverity.CRITICAL,
                    detection_rules=[
                        DetectionRule(
                            pattern=r"user_input.*\{.*\}.*completion|completion.*\{.*\}.*user_input",
                            description="Direct user input interpolation in prompts",
                            confidence_modifier=1.0
                        ),
                        DetectionRule(
                            pattern=r"prompt\s*=\s*f['\"]|prompt\s*\+=",
                            description="String concatenation or f-strings with prompts",
                            confidence_modifier=0.8
                        )
                    ],
                    remediation_steps=[
                        "Implement strict prompt templates with clear boundaries",
                        "Use parameterized prompts with type validation",
                        "Add input sanitization for special characters and instructions",
                        "Implement role-based prompt access control"
                    ],
                    false_positives=[
                        "Hardcoded template strings without user input",
                        "Internal system prompts with no user input"
                    ],
                    references=[
                        "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
                        "https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/main/content/injections.md"
                    ],
                    framework_mappings=FrameworkMapping(
                        owasp_id="A1",
                        mitre_attack_id="T1566",
                        cwe_id="CWE-917",
                        nist_id="SI-11"
                    ),
                    examples=[
                        "User input directly interpolated into system prompt",
                        "String concatenation with user input in prompts"
                    ],
                    attack_scenarios=[
                        "Attacker injects malicious instructions to override system behavior",
                        "Attacker extracts sensitive information through prompt manipulation"
                    ],
                    mitigation_guidelines=[
                        "Use strict input validation and sanitization",
                        "Implement prompt templates with clear boundaries",
                        "Add role-based access control for prompts"
                    ]
                ),
                SecurityPattern(
                    id="PROMPT-ESC-001",
                    title="Prompt Boundary Escape Vulnerability",
                    description="""
                    Critical Security Risk: Potential prompt boundary escape vulnerability.
                    The system lacks proper enforcement of prompt boundaries and role-based instructions,
                    allowing potential attackers to escape designated constraints and access unauthorized
                    capabilities.
                    """,
                    category=PatternCategory.PROMPT,
                    severity=PatternSeverity.CRITICAL,
                    detection_rules=[
                        DetectionRule(
                            pattern=r"system_prompt.*\+.*user_input|role.*\+.*user_input",
                            description="System prompt or role mixing with user input",
                            confidence_modifier=1.0
                        ),
                        DetectionRule(
                            pattern=r"instructions.*=.*user_input|context.*=.*user_input",
                            description="User input affecting system instructions",
                            confidence_modifier=0.9
                        )
                    ],
                    remediation_steps=[
                        "Implement strict role-based prompt segregation",
                        "Add validation for system-level instructions",
                        "Use separate prompt contexts for system and user inputs",
                        "Implement prompt boundary validation"
                    ],
                    false_positives=[
                        "Legitimate role-based prompt customization",
                        "Validated and sanitized instruction templates"
                    ],
                    references=[
                        "https://www.microsoft.com/en-us/security/blog/2024/01/11/prompt-injection-attacks-against-llm-systems/",
                        "https://arxiv.org/abs/2402.03544"
                    ],
                    framework_mappings=FrameworkMapping(
                        owasp_id="A1",
                        mitre_attack_id="T1566",
                        cwe_id="CWE-917",
                        nist_id="SI-11"
                    )
                )
            ],
            PatternCategory.MODEL: [
                SecurityPattern(
                    id="MODEL-SEC-001",
                    title="Insecure Model Loading",
                    description="""
                    Critical Security Risk: Insecure model loading practices detected.
                    The application loads AI models without proper validation of their source,
                    integrity, or security properties. This can lead to supply chain attacks
                    or the use of compromised models.
                    """,
                    category=PatternCategory.MODEL,
                    severity=PatternSeverity.CRITICAL,
                    detection_rules=[
                        DetectionRule(
                            pattern=r"load_model\(.*\)|from_pretrained\(.*\)",
                            description="Model loading without validation",
                            confidence_modifier=0.9
                        ),
                        DetectionRule(
                            pattern=r"model_path.*=.*input|weights.*=.*input",
                            description="Dynamic model path or weights",
                            confidence_modifier=1.0
                        )
                    ],
                    remediation_steps=[
                        "Implement model signature verification",
                        "Add hash validation for model files",
                        "Use trusted model sources only",
                        "Implement model loading access controls"
                    ],
                    false_positives=[
                        "Loading from verified internal sources",
                        "Test environments with mock models"
                    ],
                    references=[
                        "https://huggingface.co/docs/hub/security",
                        "https://github.com/microsoft/security-ai-patterns"
                    ],
                    framework_mappings=FrameworkMapping(
                        owasp_id="A1",
                        mitre_attack_id="T1566",
                        cwe_id="CWE-917",
                        nist_id="SI-11"
                    )
                )
            ],
            PatternCategory.CONFIG: [
                SecurityPattern(
                    id="CONFIG-RES-001",
                    title="Missing Resource Controls",
                    description="""
                    Critical Security Risk: Missing or insufficient AI resource controls.
                    The application lacks proper constraints on AI model resource usage,
                    potentially allowing denial of service attacks or cost escalation
                    through resource exhaustion.
                    """,
                    category=PatternCategory.CONFIG,
                    severity=PatternSeverity.CRITICAL,
                    detection_rules=[
                        DetectionRule(
                            pattern=r"max_tokens|temperature|top_p",
                            description="Missing model parameter constraints",
                            confidence_modifier=0.8
                        ),
                        DetectionRule(
                            pattern=r"timeout|retry|rate_limit",
                            description="Missing request control parameters",
                            confidence_modifier=0.9
                        )
                    ],
                    remediation_steps=[
                        "Implement token usage limits",
                        "Add request rate limiting",
                        "Set appropriate timeouts",
                        "Implement cost control mechanisms"
                    ],
                    false_positives=[
                        "Development environment configurations",
                        "Internal testing setups"
                    ],
                    references=[
                        "https://platform.openai.com/docs/guides/rate-limits",
                        "https://docs.cohere.com/docs/rate-limits"
                    ],
                    framework_mappings=FrameworkMapping(
                        owasp_id="A1",
                        mitre_attack_id="T1566",
                        cwe_id="CWE-917",
                        nist_id="SI-11"
                    )
                )
            ]
        }

    async def initialize(self):
        """Initialize the repository and load framework mappings."""
        await self.framework_manager.initialize()
        # Update framework mappings for all patterns
        for patterns in self.patterns.values():
            for pattern in patterns:
                mapping = self.framework_manager.get_framework_mapping(pattern.id)
                if mapping:
                    pattern.framework_mappings = mapping
    
    def get_patterns(self, category: PatternCategory) -> List[SecurityPattern]:
        """Get all patterns for a specific category"""
        return self.patterns.get(category, [])

    def get_pattern_by_id(self, pattern_id: str) -> Optional[SecurityPattern]:
        """Get a specific pattern by ID"""
        for patterns in self.patterns.values():
            for pattern in patterns:
                if pattern.id == pattern_id:
                    return pattern
        return None
    
    async def refresh_patterns(self):
        """Refresh patterns and framework mappings."""
        await self.framework_manager.refresh_frameworks()
        await self.initialize() 