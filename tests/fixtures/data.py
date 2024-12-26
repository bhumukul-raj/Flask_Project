"""
Data Fixtures

This module provides fixtures for data loading and saving in tests.
"""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_load_data():
    """Mock the load_data function."""
    return MagicMock(return_value={
        'users': [],
        'subjects': [],
        'sessions': {}
    })

@pytest.fixture
def mock_save_data():
    """Mock the save_data function."""
    return MagicMock(return_value=True)

@pytest.fixture
def test_data():
    """Create test data for API and service tests."""
    return {
        'subjects': [
            {
                'id': 'subject1',
                'name': 'Test Subject 1',
                'sections': [
                    {
                        'id': 'section1',
                        'name': 'Test Section 1',
                        'topics': [
                            {
                                'id': 'topic1',
                                'name': 'Test Topic 1',
                                'content': 'Test content 1'
                            }
                        ]
                    }
                ]
            }
        ]
    } 