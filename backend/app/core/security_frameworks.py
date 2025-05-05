from typing import Dict, List, Optional
import aiohttp
import json
import logging
from pathlib import Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class FrameworkMapping(BaseModel):
    """Mappings to security frameworks"""
    owasp_id: Optional[str] = None
    mitre_attack_id: Optional[str] = None
    cwe_id: Optional[str] = None
    nist_id: Optional[str] = None

class SecurityFrameworkManager:
    """Manages integration with security frameworks like OWASP, MITRE ATT&CK, and CWE."""
    
    def __init__(self):
        self.owasp_patterns: Dict[str, Dict] = {}
        self.mitre_patterns: Dict[str, Dict] = {}
        self.cwe_patterns: Dict[str, Dict] = {}
        self.nist_patterns: Dict[str, Dict] = {}
        self.cache_dir = Path("cache/security_frameworks")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize framework data from cache or fetch from sources."""
        try:
            await self._load_owasp_patterns()
            await self._load_mitre_patterns()
            await self._load_cwe_patterns()
            await self._load_nist_patterns()
        except Exception as e:
            logger.error(f"Error initializing security frameworks: {str(e)}")
            # Initialize with empty patterns if loading fails
            self.owasp_patterns = {}
            self.mitre_patterns = {}
            self.cwe_patterns = {}
            self.nist_patterns = {}
    
    async def _load_owasp_patterns(self):
        """Load OWASP LLM Top 10 patterns."""
        cache_file = self.cache_dir / "owasp_patterns.json"
        if cache_file.exists():
            with open(cache_file) as f:
                self.owasp_patterns = json.load(f)
        else:
            self.owasp_patterns = {}  # Initialize empty for now
    
    async def _load_mitre_patterns(self):
        """Load MITRE ATT&CK patterns."""
        cache_file = self.cache_dir / "mitre_patterns.json"
        if cache_file.exists():
            with open(cache_file) as f:
                self.mitre_patterns = json.load(f)
        else:
            self.mitre_patterns = {}  # Initialize empty for now
    
    async def _load_cwe_patterns(self):
        """Load CWE patterns."""
        cache_file = self.cache_dir / "cwe_patterns.json"
        if cache_file.exists():
            with open(cache_file) as f:
                self.cwe_patterns = json.load(f)
        else:
            self.cwe_patterns = {}  # Initialize empty for now
    
    async def _load_nist_patterns(self):
        """Load NIST security patterns."""
        cache_file = self.cache_dir / "nist_patterns.json"
        if cache_file.exists():
            with open(cache_file) as f:
                self.nist_patterns = json.load(f)
        else:
            self.nist_patterns = {}  # Initialize empty for now
    
    def get_framework_mapping(self, pattern_id: str) -> Optional[FrameworkMapping]:
        """Get framework mappings for a pattern."""
        # Search in each framework's patterns
        owasp_id = self._find_owasp_mapping(pattern_id)
        mitre_id = self._find_mitre_mapping(pattern_id)
        cwe_id = self._find_cwe_mapping(pattern_id)
        nist_id = self._find_nist_mapping(pattern_id)
        
        if any([owasp_id, mitre_id, cwe_id, nist_id]):
            return FrameworkMapping(
                owasp_id=owasp_id,
                mitre_attack_id=mitre_id,
                cwe_id=cwe_id,
                nist_id=nist_id
            )
        return None
    
    def _find_owasp_mapping(self, pattern_id: str) -> Optional[str]:
        """Find OWASP mapping for a pattern."""
        for pattern in self.owasp_patterns.values():
            if pattern.get("id") == pattern_id:
                return pattern.get("owasp_id")
        return None
    
    def _find_mitre_mapping(self, pattern_id: str) -> Optional[str]:
        """Find MITRE ATT&CK mapping for a pattern."""
        for pattern in self.mitre_patterns.values():
            if pattern.get("id") == pattern_id:
                return pattern.get("mitre_id")
        return None
    
    def _find_cwe_mapping(self, pattern_id: str) -> Optional[str]:
        """Find CWE mapping for a pattern."""
        for pattern in self.cwe_patterns.values():
            if pattern.get("id") == pattern_id:
                return pattern.get("cwe_id")
        return None
    
    def _find_nist_mapping(self, pattern_id: str) -> Optional[str]:
        """Find NIST mapping for a pattern."""
        for pattern in self.nist_patterns.values():
            if pattern.get("id") == pattern_id:
                return pattern.get("nist_id")
        return None
    
    async def refresh_frameworks(self):
        """Refresh all framework data from sources."""
        await self.initialize() 