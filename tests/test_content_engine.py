import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.content_engine import (
    MagicalParentingContentEngine, 
    DayTheme, 
    ContentType
)

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing"""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def content_engine(mock_openai):
    """Content engine instance with mocked OpenAI"""
    # Mock the OpenAI API key check
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        return MagicalParentingContentEngine()

class TestContentEngine:
    """Test content generation engine"""
    
    def test_get_daily_theme(self, content_engine):
        """Test daily theme selection"""
        theme = content_engine.get_daily_theme()
        assert isinstance(theme, DayTheme)
        assert theme.value in [t.value for t in DayTheme]
    
    def test_psychology_concepts_bank(self, content_engine):
        """Test psychology concepts are loaded"""
        assert len(content_engine.psychology_concepts) > 0
        assert "attachment theory" in content_engine.psychology_concepts
        assert "positive reinforcement" in content_engine.psychology_concepts
    
    def test_magical_elements_bank(self, content_engine):
        """Test magical elements are loaded"""
        assert len(content_engine.magical_elements) > 0
        assert "enchanted forest wisdom" in content_engine.magical_elements
        assert "fairy tale lessons" in content_engine.magical_elements
    
    def test_trending_topics_bank(self, content_engine):
        """Test trending topics are loaded"""
        assert len(content_engine.trending_topics) > 0
        assert "toddler tantrums" in content_engine.trending_topics
        assert "bedtime struggles" in content_engine.trending_topics

@pytest.mark.asyncio
async def test_generate_carousel_content_fallback(content_engine):
    """Test fallback content generation when AI fails"""
    # Mock OpenAI to fail
    with patch.object(content_engine, '_call_openai', side_effect=Exception("API Error")):
        carousel = await content_engine.generate_carousel_content(DayTheme.MAGICAL_MONDAY, "test topic")
        
        assert carousel.title == "Quick Tips for test topic"
        assert len(carousel.slides) == 5
        assert carousel.psychology_concept == "general support"
        assert carousel.magical_element == "gentle encouragement"

@pytest.mark.asyncio
async def test_generate_video_content_fallback(content_engine):
    """Test fallback video generation when AI fails"""
    # Mock OpenAI to fail
    with patch.object(content_engine, '_call_openai', side_effect=Exception("API Error")):
        video = await content_engine.generate_video_content(DayTheme.MAGICAL_MONDAY, "test topic")
        
        assert video.title == "Quick Video: test topic"
        assert len(video.slides) == 4
        assert video.psychology_concept == "general support"
        assert video.magical_element == "encouraging tone"

def test_day_theme_enum():
    """Test day theme enum values"""
    themes = list(DayTheme)
    assert len(themes) == 7
    
    expected_themes = [
        "magical_monday_wisdom",
        "tiny_tales_tuesday", 
        "wonder_wednesday",
        "thoughtful_thursday",
        "fantasy_friday",
        "story_saturday",
        "serene_sunday"
    ]
    
    for theme in themes:
        assert theme.value in expected_themes

def test_content_type_enum():
    """Test content type enum values"""
    types = list(ContentType)
    assert len(types) == 3
    
    expected_types = ["carousel", "video", "story"]
    for content_type in types:
        assert content_type.value in expected_types

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
