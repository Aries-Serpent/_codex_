"""
Test Intelligent Analyzer

Test module for intelligent analyzer.
"""

#!/usr/bin/env python3
"""Test suite for intelligent audio analyzer.

Test Data Strategy:
This test suite uses 1KB of zero bytes as mock audio data. While this doesn't
represent realistic audio structure, it's sufficient for unit testing the
analyzer's workflow, error handling, and interface contracts.

For more robust testing:
- Integration tests should use minimal valid WAV/MP3 file headers with test data
- Mock the audio library's load function to return controlled numpy arrays
- Use real audio fixtures for end-to-end validation

The current approach prioritizes fast unit tests over format validation.
"""

import pytest
from services.audio.analysis.intelligent_analyzer import (
    IntelligentAudioAnalyzer,
    AudioAnalysis,
    ProfileMatch
)

# Mock binary audio data for testing (1KB of zeros)
# Note: Not realistic audio format, but sufficient for workflow unit tests
MOCK_AUDIO_DATA = b'\x00' * 1024


class TestIntelligentAudioAnalyzer:
    """Test cases for IntelligentAudioAnalyzer."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes with profiles."""
        analyzer = IntelligentAudioAnalyzer()
        assert len(analyzer.profiles) > 0
        assert analyzer.profiles[0].name in ['speech', 'music', 'ambient']
    
    def test_analyze_file(self, tmp_path):
        """Test file analysis with mock audio file."""
        analyzer = IntelligentAudioAnalyzer()
        test_file = tmp_path / "test.mp3"
        
        # Create a minimal binary file (not actual audio, but better than text)
        # In production, this would use a minimal valid WAV/MP3 or mock the audio library
        test_file.write_bytes(MOCK_AUDIO_DATA)
        
        analysis = analyzer.analyze_file(test_file)
        
        assert isinstance(analysis, AudioAnalysis)
        assert analysis.file_path == test_file
        assert analysis.content_type in ['speech', 'music', 'ambient', 'mixed']
        assert 0 <= analysis.quality_score <= 10
    
    def test_select_profile(self, tmp_path):
        """Test profile selection."""
        analyzer = IntelligentAudioAnalyzer()
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(MOCK_AUDIO_DATA)
        
        analysis = analyzer.analyze_file(test_file)
        profile_match = analyzer.select_profile(analysis)
        
        assert isinstance(profile_match, ProfileMatch)
        assert profile_match.confidence > 0
        assert len(profile_match.reason) > 0
    
    def test_aggressive_mode(self, tmp_path):
        """Test aggressive mode selection."""
        analyzer = IntelligentAudioAnalyzer()
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(MOCK_AUDIO_DATA)
        
        analysis = analyzer.analyze_file(test_file)
        normal_match = analyzer.select_profile(analysis, aggressive=False)
        aggressive_match = analyzer.select_profile(analysis, aggressive=True)
        
        assert aggressive_match.confidence >= normal_match.confidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
