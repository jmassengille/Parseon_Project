"""
Custom exceptions for Parseon.
"""

class ParseonError(Exception):
    """Base exception for all Parseon errors"""
    pass

class ValidationError(ParseonError):
    """Exception raised when validation fails"""
    pass

class FindingValidatorError(ParseonError):
    """Exception raised when finding validation process fails"""
    pass

class ConfigurationError(ParseonError):
    """Exception raised when configuration is invalid"""
    pass

class ServiceConnectionError(ParseonError):
    """Exception raised when connection to external service fails"""
    pass

class AssessmentError(Exception):
    """Base exception for assessment-related errors"""
    pass

class GroundingError(Exception):
    """Exception raised when grounding process fails"""
    pass

class PatternMatcherError(Exception):
    """Exception raised when pattern matching fails"""
    pass

class DatabaseError(Exception):
    """Exception raised when database operations fail"""
    pass

class AIAnalysisError(Exception):
    """Exception raised when AI analysis fails"""
    pass 