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
        # Use timeout to prevent hanging API calls
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=60.0  # 60 second timeout for API calls
        )
        # Default to faster model if not specified
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    
    async def analyze_code(self, code: str, context: str) -> List[VulnerabilityFinding]:
        """Analyze code for AI security vulnerabilities using the base model"""
        
        system_prompt = (
            "You are an AI security auditor analyzing code for vulnerabilities. Respond with JSON containing an array of findings. "
            "Each finding must include: title, description, severity (LOW/MEDIUM/HIGH/CRITICAL), category, code_snippet, recommendation. "
            "Only report actual security issues. Ignore API keys that use environment variables. "
            "Focus on: prompt injection, lack of input validation, insecure configuration, rate limiting, error handling."
        )
        
        user_prompt = (
            f"Identify AI security vulnerabilities in this code. Be precise and concise.\n\n<code>\n{code}\n</code>\nContext: {context}"
        )
        
        return await self._analyze_with_llm(system_prompt, user_prompt)
    
    async def analyze_config(self, config: str) -> List[VulnerabilityFinding]:
        """Analyze configuration for AI security vulnerabilities using the base model"""
        findings = []
        
        system_prompt = (
            "You are an AI security auditor analyzing configuration for vulnerabilities. Respond with JSON containing an array of findings. "
            "Each finding must include: title, description, severity (LOW/MEDIUM/HIGH/CRITICAL), category, code_snippet, recommendation. "
            "Only report actual security issues. Ignore API keys that use environment variables. "
            "Focus on: insecure model settings, overly permissive parameters, missing rate limits."
        )

        user_prompt = (
            f"Identify AI security vulnerabilities in this configuration. Be precise and concise.\n\n<config>\n{config}\n</config>"
        )
        
        llm_findings = await self._analyze_with_llm(system_prompt, user_prompt)
        return findings + llm_findings
    
    async def _analyze_with_llm(self, system_prompt: str, user_prompt: str) -> List[VulnerabilityFinding]:
        """Helper method that handles the actual LLM call and parsing logic"""
        try:
            # Try with response_format first (with streaming for faster response)
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,  # Reduced temperature for faster, more consistent responses
                    max_tokens=2000,  # Set a reasonable limit to avoid excessive generation
                    response_format={"type": "json_object"},
                    stream=True  # Enable streaming for faster time-to-first-token
                )
                
                # Process the stream
                collected_messages = []
                async for chunk in response:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                        collected_messages.append(chunk.choices[0].delta.content)
                response_text = "".join(collected_messages)
                
                # Calculate tokens for metrics (estimate based on length)
                prompt_tokens = len(system_prompt + user_prompt) // 4
                completion_tokens = len(response_text) // 4
                self.token_usage["prompt_tokens"] += prompt_tokens
                self.token_usage["completion_tokens"] += completion_tokens
                
            except Exception as e:
                # If json_object format fails, fall back to regular completion
                logger.warning(f"JSON format request failed: {str(e)}. Falling back to standard format.")
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,  # Lower temperature for faster, more consistent responses
                    stream=False  # Disable streaming in fallback
                )
            
            # Update token usage
            if hasattr(response, 'usage'):
                self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage["completion_tokens"] += response.usage.completion_tokens
            
            # If we don't already have response_text from streaming
            if 'response_text' not in locals():
                response_text = response.choices[0].message.content
            
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
        """Parse LLM response text into structured VulnerabilityFinding objects"""
        findings = []
        try:
            # Attempt to parse as JSON
            response_data = json.loads(response_text)
            
            # Handle if the response is a dict with a 'findings' key
            if isinstance(response_data, dict) and 'findings' in response_data:
                items = response_data['findings']
            # Handle if the response is a list
            elif isinstance(response_data, list):
                items = response_data
            else:
                # Check if we have another place where findings might be stored
                for key in response_data.keys():
                    if isinstance(response_data[key], list) and len(response_data[key]) > 0:
                        if isinstance(response_data[key][0], dict) and 'title' in response_data[key][0]:
                            items = response_data[key]
                            break
                else:
                    # No list of findings found
                    logger.warning("No structured findings found in response")
                    return []
                    
            # Process each finding
            for idx, item in enumerate(items):
                try:
                    # Required fields with fallbacks
                    title = item.get('title', f"Finding {idx+1}")
                    
                    # Fields with defaults if missing
                    description = item.get('description', '')
                    severity = item.get('severity', 'MEDIUM').upper()
                    category = self._normalize_category(item.get('category', 'GENERAL'))
                    
                    # Extract code snippets
                    if 'code_snippets' in item and isinstance(item['code_snippets'], list):
                        code_snippets = item['code_snippets']
                    elif 'code_snippet' in item:
                        code_snippets = [item['code_snippet']]
                    else:
                        code_snippets = []
                    
                    # Extract recommendation
                    recommendation = item.get('recommendation', 'No specific recommendation provided.')
                
                    # Create finding
                    finding = VulnerabilityFinding(
                        id=f"finding-{idx}",
                        title=title,
                        description=description,
                        severity=severity,
                        category=category,
                        code_snippets=code_snippets,
                        recommendation=recommendation,
                        confidence=self._calculate_confidence(item)
                    )
                    findings.append(finding)
                except Exception as e:
                    logger.error(f"Error parsing finding {idx}: {str(e)}")
            
            return findings
        
        except Exception as e:
            logger.error(f"Error parsing findings from response: {str(e)}")
            return []
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category names to standard format"""
        category = category.upper().replace(' ', '_')
        
        # Map to standard categories
        category_map = {
            'API': 'API_SECURITY',
            'API_SECURITY': 'API_SECURITY',
            'PROMPT': 'PROMPT_SECURITY',
            'PROMPT_INJECTION': 'PROMPT_SECURITY',
            'PROMPT_SECURITY': 'PROMPT_SECURITY',
            'CONFIG': 'CONFIGURATION',
            'CONFIGURATION': 'CONFIGURATION',
            'ERROR': 'ERROR_HANDLING',
            'ERROR_HANDLING': 'ERROR_HANDLING'
        }
        
        # Try to match against map
        for key, value in category_map.items():
            if key in category:
                return value
        
        return 'GENERAL_SECURITY'
    
    def _calculate_confidence(self, finding: Dict) -> float:
        """Calculate a confidence score for the finding based on content quality"""
        confidence = 0.8  # Default confidence
        
        # Adjust based on recommendation quality
        if 'recommendation' in finding and len(finding.get('recommendation', '')) > 50:
            confidence += 0.05
            
        # Adjust based on description quality
        if 'description' in finding and len(finding.get('description', '')) > 100:
            confidence += 0.05
            
        # Cap at 1.0
        return min(1.0, confidence) 