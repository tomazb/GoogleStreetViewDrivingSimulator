"""Pytest configuration and shared fixtures."""

from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "test_api_key_12345"


@pytest.fixture
def sample_coordinates():
    """Provide sample coordinates for testing."""
    return [
        (40.7128, -74.0060),  # New York
        (40.7589, -73.9851),  # Times Square
        (40.7614, -73.9776),  # Central Park
    ]


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def mock_requests_session():
    """Mock requests.Session for API tests."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "steps": [
                            {"polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"}},  # Real polyline
                        ]
                    }
                ]
            }
        ],
    }
    mock_session.get.return_value = mock_response
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=False)
    mock_session.close = Mock()
    return mock_session
