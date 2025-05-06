"""
Direct base model analyzer for AI security vulnerabilities

This module provides functionality to analyze code and configurations using
a large language model directly, with results parsed into structured findings.
"""

from typing import Dict, List, Optional, Any
import os
import logging
import json
import re
from openai import AsyncOpenAI
from app.schemas.assessment import VulnerabilityFinding

logger = logging.getLogger(__name__)

class BaseModelAnalyzer:
    """Analyzes code and configurations using LLM for AI security vulnerabilities"""
    
    def __init__(self):
        """Initialize with OpenAI client"""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-16k")
        self.token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    
    async def analyze_code(self, code: str, context: str) -> List[VulnerabilityFinding]:
        """Analyze code for AI security vulnerabilities using the base model"""
        print(f"\n---- DEBUG: Base model analysis for {context} ----")
        
        system_prompt = (
            "You are an expert AI security auditor. Review the following code for any possible, theoretical, or even minor AI security vulnerabilities. "
            "Consider prompt injection, lack of input validation, insecure configuration, excessive permissions, or any other risk. "
            "Use your full reasoning and creativity. Err on the side of caution: if there is any doubt, report a potential vulnerability. "
            "Do not flag API keys that are environment variable references (e.g., OPENAI_API_KEY) as vulnerabilities. Only flag hardcoded secrets if the value starts with 'sk-' or looks like a real secret. "
            "If rate limiting logic is present, even as a stub or placeholder (e.g., allow_request), do not flag as a vulnerability unless there is no rate limiting logic at all. "
            "If input validation and sanitization are present, do not flag unless there is clear evidence of missing or weak validation. "
            "Respond with a JSON array of findings, and you may include a brief narrative summary before the JSON if you wish. "
            "Each finding should include: title, description, severity, category, code_snippet, recommendation."
        )
        
        user_prompt = (
            f"Here is a real-world code sample from an AI-integrated application. "
            f"Please identify and describe all possible security vulnerabilities, even if they are only potential or minor risks. "
            f"Use your best judgment and be thorough.\n\n<code>\n{code}\n</code>\nContext: {context}"
        )
        
        return await self._analyze_with_llm(system_prompt, user_prompt)
    
    async def analyze_config(self, config: str) -> List[VulnerabilityFinding]:
        """Analyze configuration for AI security vulnerabilities using the base model"""
        # Regex-based check for hardcoded OpenAI API keys
        import json as _json
        findings = []
        try:
            config_dict = _json.loads(config)
            api_key = config_dict.get("api_key", "")
            import re
            if isinstance(api_key, str) and re.match(r"^sk-[a-zA-Z0-9]{20,}$", api_key):
                findings.append(VulnerabilityFinding(
                    id="api_key_hardcoded",
                    title="Hardcoded OpenAI API Key",
                    description="The API key is hardcoded in the configuration. Use environment variables or a secure key management system instead.",
                    severity="HIGH",
                    category="API_SECURITY",
                    code_snippets=[f'"api_key": "{api_key}"'],
                    recommendation="Store API keys in environment variables or a secure key vault. Never hardcode secrets in config files.",
                    confidence=1.0
                ))
        except Exception:
            pass  # If config is not valid JSON, skip static check
        system_prompt = (
            "You are an expert AI security auditor. Review the following configuration for any possible, theoretical, or even minor AI security vulnerabilities. "
            "Consider insecure model settings, overly permissive parameters, missing rate limits, insecure API keys, or any other risk. "
            "Use your full reasoning and creativity. Err on the side of caution: if there is any doubt, report a potential vulnerability. "
            "Do not flag API keys as hardcoded if the value is a variable reference (e.g., OPENAI_API_KEY, process.env.OPENAI_API_KEY, os.environ['OPENAI_API_KEY']). Only flag as hardcoded if the value starts with 'sk-' or looks like a real secret. "
            "Respond with a JSON array of findings, and you may include a brief narrative summary before the JSON if you wish. "
            "Each finding should include: title, description, severity, category, code_snippet, recommendation."
        )
        user_prompt = (
            f"Here is a real-world configuration file from an AI-integrated application. "
            f"Please identify and describe all possible security vulnerabilities, even if they are only potential or minor risks. "
            f"Use your best judgment and be thorough.\n\n<config>\n{config}\n</config>"
        )
        llm_findings = await self._analyze_with_llm(system_prompt, user_prompt)
        return findings + llm_findings
    
    async def _analyze_with_llm(self, system_prompt: str, user_prompt: str) -> List[VulnerabilityFinding]:
        """Helper method that handles the actual LLM call and parsing logic"""
        try:
            print("\n==== SYSTEM PROMPT ====")
            print(system_prompt)
            print("\n==== USER PROMPT ====")
            print(user_prompt)
            
            # Try with response_format first
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
            except Exception as e:
                # If json_object format fails, fall back to regular completion
                logger.warning(f"JSON format request failed: {str(e)}. Falling back to standard format.")
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
            
            # Update token usage
            if hasattr(response, 'usage'):
                self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage["completion_tokens"] += response.usage.completion_tokens
            
            response_text = response.choices[0].message.content
            print("\n==== RAW LLM RESPONSE ====")
            print(response_text)
            print("========================\n")
            
            # Try to clean up the response if it's not valid JSON
            try:
                json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, look for JSON array in the response
                json_match = re.search(r'(\[\s*\{.*\}\s*\])', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
                    logger.info("Extracted JSON array from response")
            
            # Parse findings
            findings = self._parse_findings(response_text)
            print(f"Found {len(findings)} issues with base model analysis")
            
            return findings
            
        except Exception as e:
            logger.error(f"Error in base model analysis: {str(e)}")
            # Try to parse what we got anyway
            try:
                if locals().get('response_text'):
                    findings = self._parse_findings(response_text)
                    if findings:
                        return findings
            except Exception:
                pass
            return []
    
    def _parse_findings(self, response_text: str) -> List[VulnerabilityFinding]:
        """Parse LLM response into VulnerabilityFinding objects"""
        findings = []
        
        # Check if response indicates no findings (common patterns)
        no_findings_patterns = [
            r"no .*vulnerabilities",
            r"no .*security issues",
            r"no .*found",
            r"properly handles security",
            r"secure implementation",
            r"no .* detected"
        ]
        
        # If the response indicates no findings, return an empty list
        for pattern in no_findings_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                print(f"Response indicates no security issues found")
                return []
        
        # Check if we have a valid JSON response
        try:
            # First try to parse the entire response as JSON
            try:
                data = json.loads(response_text)
                if isinstance(data, dict) and "findings" in data:
                    data = data["findings"]  # Handle {"findings": [...]} format
                
                # Process findings from JSON
                if isinstance(data, list):
                    for i, finding_data in enumerate(data):
                        category = self._normalize_category(finding_data.get("category", "CONFIGURATION"))
                        severity = self._normalize_severity(finding_data.get("severity", "MEDIUM"))
                        
                        finding = VulnerabilityFinding(
                            id=f"finding_{i+1}",
                            title=finding_data.get("title", "Unnamed Finding"),
                            description=finding_data.get("description", "No description provided"),
                            severity=severity,
                            category=category,
                            code_snippets=[finding_data.get("code_snippet", "No code snippet provided")],
                            recommendation=finding_data.get("recommendation", "No recommendation provided"),
                            confidence=float(finding_data.get("confidence", 0.5))
                        )
                        findings.append(finding)
                        print(f"  - {finding.title} ({finding.severity}): {finding.confidence}")
                    
                    return findings
            except json.JSONDecodeError:
                # If the entire response is not JSON, try to extract JSON fragments
                json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                    try:
                        data = json.loads(json_text)
                        # Process JSON array findings (same as above)
                        for i, finding_data in enumerate(data):
                            category = self._normalize_category(finding_data.get("category", "CONFIGURATION"))
                            severity = self._normalize_severity(finding_data.get("severity", "MEDIUM"))
                            
                            finding = VulnerabilityFinding(
                                id=f"finding_{i+1}",
                                title=finding_data.get("title", "Unnamed Finding"),
                                description=finding_data.get("description", "No description provided"),
                                severity=severity,
                                category=category,
                                code_snippets=[finding_data.get("code_snippet", "No code snippet provided")],
                                recommendation=finding_data.get("recommendation", "No recommendation provided"),
                                confidence=float(finding_data.get("confidence", 0.5))
                            )
                            findings.append(finding)
                            print(f"  - {finding.title} ({finding.severity}): {finding.confidence}")
                        
                        if findings:
                            return findings
                    except json.JSONDecodeError:
                        pass  # Continue to fallback extraction
            
            # Fallback to parsing numbered list format
            if "1." in response_text and "vulnerabilit" in response_text.lower():
                # Extract numbered findings
                numbers = re.findall(r'\n\s*(\d+)\.\s', response_text)
                if numbers:
                    # Split by numbered sections
                    sections = re.split(r'\n\s*\d+\.\s', response_text)
                    # First section is usually just an intro, skip it
                    sections = sections[1:] if len(sections) > 1 else sections
                    
                    for i, section in enumerate(sections):
                        section = section.strip()
                        if not section:
                            continue
                        
                        # Extract title
                        title_match = re.search(r'\*\*(.*?)\*\*', section)
                        title = title_match.group(1) if title_match else f"Finding {i+1}"
                        
                        # Extract description
                        description_pattern = r'\*\*Description\*\*:\s*(.*?)(?:\n\s*\*\*|\Z)'
                        description_match = re.search(description_pattern, section, re.DOTALL | re.IGNORECASE)
                        description = description_match.group(1).strip() if description_match else section[:200]
                        
                        # Extract severity
                        severity_pattern = r'\*\*Severity\*\*:\s*(.*?)(?:\n\s*\*\*|\Z)'
                        severity_match = re.search(severity_pattern, section, re.DOTALL | re.IGNORECASE)
                        severity = severity_match.group(1).strip() if severity_match else "MEDIUM"
                        
                        # Extract category
                        category_pattern = r'\*\*Category\*\*:\s*(.*?)(?:\n\s*\*\*|\Z)'
                        category_match = re.search(category_pattern, section, re.DOTALL | re.IGNORECASE)
                        category = category_match.group(1).strip() if category_match else "PROMPT_SECURITY"
                        
                        # Extract code snippet
                        code_pattern = r'```(?:python)?\s*(.*?)\s*```'
                        code_match = re.search(code_pattern, section, re.DOTALL)
                        code_snippet = code_match.group(1).strip() if code_match else "No code snippet provided"
                        
                        # Extract recommendation
                        recommendation_pattern = r'\*\*Recommendation\*\*:\s*(.*?)(?:\n\s*\*\*|\Z)'
                        recommendation_match = re.search(recommendation_pattern, section, re.DOTALL | re.IGNORECASE)
                        recommendation = recommendation_match.group(1).strip() if recommendation_match else "No recommendation provided"
                        
                        # Normalize
                        normalized_category = self._normalize_category(category)
                        normalized_severity = self._normalize_severity(severity)
                        
                        finding = VulnerabilityFinding(
                            id=f"finding_{i+1}",
                            title=title,
                            description=description, 
                            severity=normalized_severity,
                            category=normalized_category,
                            code_snippets=[code_snippet],
                            recommendation=recommendation,
                            confidence=0.8  # Higher confidence for well-structured findings
                        )
                        findings.append(finding)
                        print(f"  - {finding.title} ({finding.severity}): {finding.confidence}")
                
                if findings:
                    return findings
            
        except Exception as e:
            logger.error(f"Error processing findings: {str(e)}")
        
        # If we got here and still have no findings, try more aggressive pattern matching
        # This is a final fallback attempt
        try:
            if "vulnerability" in response_text.lower() or "security issue" in response_text.lower():
                lines = response_text.split("\n")
                current_finding = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this is a new finding (starts with a number or has a title pattern)
                    if re.match(r'^\d+\.', line) or "**" in line:
                        # Save the previous finding if any
                        if current_finding.get("title"):
                            category = self._normalize_category(current_finding.get("category", "PROMPT_SECURITY"))
                            severity = self._normalize_severity(current_finding.get("severity", "MEDIUM"))
                            
                            finding = VulnerabilityFinding(
                                id=f"finding_{len(findings)+1}",
                                title=current_finding.get("title", "Unnamed Finding"),
                                description=current_finding.get("description", "No description provided"),
                                severity=severity,
                                category=category,
                                code_snippets=[current_finding.get("code_snippet", "No code snippet provided")],
                                recommendation=current_finding.get("recommendation", "No recommendation provided"),
                                confidence=0.6  # Lower confidence for loosely structured findings
                            )
                            findings.append(finding)
                        
                        # Start a new finding
                        current_finding = {"title": line.split(".", 1)[-1].strip()}
                    
                    # Check for known patterns to identify fields
                    elif "description" in line.lower() and ":" in line:
                        current_finding["description"] = line.split(":", 1)[-1].strip()
                    elif "severity" in line.lower() and ":" in line:
                        current_finding["severity"] = line.split(":", 1)[-1].strip()
                    elif "category" in line.lower() and ":" in line:
                        current_finding["category"] = line.split(":", 1)[-1].strip()
                    elif "recommendation" in line.lower() and ":" in line:
                        current_finding["recommendation"] = line.split(":", 1)[-1].strip()
                    elif "code snippet" in line.lower() and ":" in line:
                        current_finding["code_snippet"] = line.split(":", 1)[-1].strip()
                
                # Save the last finding if any
                if current_finding.get("title"):
                    category = self._normalize_category(current_finding.get("category", "PROMPT_SECURITY"))
                    severity = self._normalize_severity(current_finding.get("severity", "MEDIUM"))
                    
                    finding = VulnerabilityFinding(
                        id=f"finding_{len(findings)+1}",
                        title=current_finding.get("title", "Unnamed Finding"),
                        description=current_finding.get("description", "No description provided"),
                        severity=severity,
                        category=category,
                        code_snippets=[current_finding.get("code_snippet", "No code snippet provided")],
                        recommendation=current_finding.get("recommendation", "No recommendation provided"),
                        confidence=0.6  # Lower confidence for loosely structured findings
                    )
                    findings.append(finding)
        
        except Exception as e:
            logger.error(f"Error in fallback parsing: {str(e)}")
        
        return findings
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category to match expected values"""
        category_map = {
            "api": "API_SECURITY",
            "api_security": "API_SECURITY",
            "api security": "API_SECURITY",
            
            "prompt": "PROMPT_SECURITY",
            "prompt_security": "PROMPT_SECURITY",
            "prompt security": "PROMPT_SECURITY",
            "prompt injection": "PROMPT_SECURITY",
            
            "config": "CONFIGURATION",
            "configuration": "CONFIGURATION",
            "setting": "CONFIGURATION",
            "settings": "CONFIGURATION",
            
            "error": "ERROR_HANDLING",
            "error_handling": "ERROR_HANDLING",
            "error handling": "ERROR_HANDLING",
            "exception": "ERROR_HANDLING",
            "exception_handling": "ERROR_HANDLING",
            "exception handling": "ERROR_HANDLING"
        }
        
        # If the category is already normalized, return it
        if category.upper() in ["API_SECURITY", "PROMPT_SECURITY", "CONFIGURATION", "ERROR_HANDLING"]:
            return category.upper()
        
        # Try to match category to a known value
        category_lower = category.lower()
        for key, value in category_map.items():
            if key in category_lower:
                return value
        
        # Default to API_SECURITY if unknown
        return "API_SECURITY"
    
    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity to match expected values"""
        severity_map = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
            "info": "LOW",
            "informational": "LOW",
            "warning": "MEDIUM",
            "severe": "HIGH"
        }
        
        # If the severity is already normalized, return it
        if severity.upper() in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            return severity.upper()
        
        # Try to match severity to a known value
        severity_lower = severity.lower()
        for key, value in severity_map.items():
            if key in severity_lower:
                return value
        
        # Default to MEDIUM if unknown
        return "MEDIUM" 