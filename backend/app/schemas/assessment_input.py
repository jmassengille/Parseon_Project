from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
from enum import Enum
from app.schemas.assessment import ScanMode

class AIProvider(str, Enum):
    OPENAI = "openai"
    # Future providers
    # AZURE_OPENAI = "azure_openai"
    # ANTHROPIC = "anthropic"

class ConfigType(str, Enum):
    ENV_FILE = "env_file"
    JSON_CONFIG = "json_config"
    MARKDOWN_DOC = "markdown_doc"
    CODE_SNIPPET = "code_snippet"

class SecurityAssessmentInput(BaseModel):
    """
    Input schema for security assessment requests.
    
    This model defines the structure of security assessment inputs, including:
    - Organization and project metadata
    - AI provider information
    - Configuration files (env files, JSON configs)
    - Implementation details
    - Architecture description
    
    The input is designed to capture all relevant information needed to assess
    security risks in AI implementations.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_name": "Acme Corp",
                "project_name": "Customer Service Bot",
                "ai_provider": "openai",
                "scan_mode": "COMPREHENSIVE",
                "configs": {
                    "env_file": "OPENAI_API_KEY=sk-***\nMAX_TOKENS=500",
                    "json_config": '{"temperature": 0.7, "max_tokens": 500}'
                },
                "implementation_details": {
                    "prompt_handling": "def sanitize_prompt(prompt): ...",
                    "error_handling": "try: response = openai.Completion.create(...)"
                },
                "architecture_description": "API endpoint that validates user input, sends to GPT-3.5-turbo, sanitizes response..."
            }
        }
    )

    organization_name: str = Field(description="Name of the organization")
    project_name: str = Field(description="Name of the project being assessed")
    ai_provider: AIProvider = Field(description="AI provider being used")
    scan_mode: ScanMode = Field(default=ScanMode.COMPREHENSIVE, description="Assessment scan mode")
    
    # Configuration Files
    configs: Dict[ConfigType, str] = Field(
        description="Configuration content by type (e.g., env files, JSON configs)",
        json_schema_extra={
            "example": {
                "env_file": "OPENAI_API_KEY=sk-***\nMAX_TOKENS=500\n",
                "json_config": '{"temperature": 0.7, "max_tokens": 500}'
            }
        }
    )
    
    # Code Implementation Details
    implementation_details: Optional[Dict[str, str]] = Field(
        default=None,
        description="Relevant code snippets or implementation details",
        json_schema_extra={
            "example": {
                "prompt_handling": "def sanitize_prompt(prompt): ...",
                "error_handling": "try: response = openai.Completion.create(...)"
            }
        }
    )
    
    # Architecture Description
    architecture_description: Optional[str] = Field(
        default=None,
        description="High-level description of the AI implementation architecture"
    ) 