import pytest
import asyncio
from app.core.knowledge_base import KnowledgeBase, SecurityPattern
import json
from pathlib import Path

@pytest.fixture
def knowledge_base():
    return KnowledgeBase(test_mode=True)

@pytest.mark.asyncio
async def test_initialize_knowledge_base(knowledge_base):
    """Test that the knowledge base initializes properly with test data."""
    await knowledge_base.initialize()
    assert len(knowledge_base.patterns) > 0, "Knowledge base should contain patterns after initialization"

@pytest.mark.asyncio
async def test_owasp_ai_patterns(knowledge_base):
    """Test that OWASP AI patterns are properly loaded and processed."""
    await knowledge_base.initialize()
    owasp_patterns = knowledge_base.get_patterns_by_source("owasp_ai")
    
    assert len(owasp_patterns) > 0, "Should have loaded OWASP AI patterns"
    
    # Verify pattern structure
    pattern = owasp_patterns[0]
    assert pattern.id.startswith("owasp_ai_"), "Pattern ID should be prefixed with source"
    assert pattern.source == "owasp_ai", "Pattern source should be set"
    assert pattern.category in ["Model Security", "Data Security", "Infrastructure Security", "General Security"], "Pattern should have valid category"

@pytest.mark.asyncio
async def test_mitre_atlas_patterns(knowledge_base):
    """Test that MITRE ATLAS patterns are properly loaded and processed."""
    await knowledge_base.initialize()
    atlas_patterns = knowledge_base.get_patterns_by_source("mitre_atlas")
    
    assert len(atlas_patterns) > 0, "Should have loaded MITRE ATLAS patterns"
    
    # Verify pattern structure
    pattern = atlas_patterns[0]
    assert pattern.id.startswith("mitre_atlas_"), "Pattern ID should be prefixed with source"
    assert pattern.source == "mitre_atlas", "Pattern source should be set"
    assert pattern.severity in ["critical", "high", "medium", "low"], "Pattern should have valid severity"

@pytest.mark.asyncio
async def test_mitre_matrix_patterns(knowledge_base):
    """Test that MITRE ATLAS matrix patterns are properly loaded and processed."""
    await knowledge_base.initialize()
    matrix_patterns = knowledge_base.get_patterns_by_source("mitre_matrix")
    
    assert len(matrix_patterns) > 0, "Should have loaded MITRE matrix patterns"
    
    # Verify pattern structure
    pattern = matrix_patterns[0]
    assert pattern.id.startswith("mitre_matrix_"), "Pattern ID should be prefixed with source"
    assert pattern.source == "mitre_matrix", "Pattern source should be set"
    assert pattern.severity in ["critical", "high", "medium", "low"], "Pattern should have valid severity"

@pytest.mark.asyncio
async def test_pattern_persistence(knowledge_base):
    """Test that patterns can be saved and loaded from file."""
    # Add a test pattern
    test_pattern = SecurityPattern(
        id="test_pattern_1",
        category="Test Category",
        description="Test Description",
        severity="medium",
        pattern="Test Pattern",
        examples=["Example 1"],
        mitigation="Test Mitigation",
        references=["Reference 1"],
        source="test"
    )
    knowledge_base.add_pattern(test_pattern)
    
    # Create new instance and load patterns
    new_kb = KnowledgeBase(knowledge_base.patterns_file, test_mode=True)
    await new_kb.initialize()
    
    # Verify pattern was loaded
    loaded_pattern = new_kb.get_pattern("test_pattern_1")
    assert loaded_pattern is not None, "Pattern should be loaded from file"
    assert loaded_pattern.description == "Test Description", "Pattern description should match"

@pytest.mark.asyncio
async def test_pattern_categories(knowledge_base):
    """Test that patterns can be retrieved by category."""
    await knowledge_base.initialize()
    
    # Get all unique categories
    categories = set(pattern.category for pattern in knowledge_base.patterns.values())
    assert len(categories) > 0, "Should have multiple categories"
    
    # Test getting patterns by category
    for category in categories:
        patterns = knowledge_base.get_patterns_by_category(category)
        assert len(patterns) > 0, f"Should have patterns for category {category}"
        assert all(p.category == category for p in patterns), "All patterns should match the requested category" 