"""
Unit tests for LinkedIn Agent

Run with: pytest tests/test_linkedin_agent.py -v
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from linkedin_agent import brave_search, get_used_themes


class TestBraveSearch:
    """Tests for Brave Search integration"""
    
    @patch.dict(os.environ, {'BRAVE_SEARCH_API_KEY': 'test_key'})
    @patch('linkedin_agent.requests.get')
    def test_brave_search_success(self, mock_get):
        """Test successful Brave Search API call"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'web': {'results': [{'title': 'Test Result'}]}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = brave_search("test query")
        result_data = json.loads(result)
        
        assert 'web' in result_data
        assert mock_get.called
    
    @patch.dict(os.environ, {}, clear=True)
    def test_brave_search_no_api_key(self):
        """Test Brave Search without API key"""
        result = brave_search("test query")
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert 'BRAVE_SEARCH_API_KEY' in result_data['error']


class TestGetUsedThemes:
    """Tests for Google Sheets integration"""
    
    @patch('linkedin_agent.get_recent_themes')
    def test_get_used_themes_success(self, mock_get_themes):
        """Test successful retrieval of themes"""
        mock_get_themes.return_value = ['Theme 1', 'Theme 2']
        
        result = get_used_themes()
        result_data = json.loads(result)
        
        assert 'themes' in result_data
        assert len(result_data['themes']) == 2
        assert mock_get_themes.called
    
    @patch('linkedin_agent.get_recent_themes')
    def test_get_used_themes_error(self, mock_get_themes):
        """Test error handling when retrieving themes"""
        mock_get_themes.side_effect = Exception("Connection error")
        
        result = get_used_themes()
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert 'themes' in result_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
