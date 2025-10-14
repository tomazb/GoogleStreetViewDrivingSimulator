"""Unit tests for API functions."""

from unittest.mock import Mock, patch

import pytest

from streetview_simulator.api import (
    _coerce_bool,
    _coerce_coordinate,
    _coerce_float,
    _normalise_size,
    _resolve_api_key,
    build_coords,
    fetch_route_coordinates,
    get_heading,
    unique,
)


class TestResolveApiKey:
    """Test suite for API key resolution."""

    def test_explicit_key_used(self):
        """Test that explicit key takes precedence."""
        key = _resolve_api_key("my_explicit_key")
        assert key == "my_explicit_key"

    def test_environment_key_used(self, monkeypatch):
        """Test that environment variable is used when no explicit key."""
        monkeypatch.setenv("GOOGLE_STREETVIEW_API_KEY", "env_key_value")
        key = _resolve_api_key()
        assert key == "env_key_value"

    def test_explicit_overrides_environment(self, monkeypatch):
        """Test that explicit key overrides environment variable."""
        monkeypatch.setenv("GOOGLE_STREETVIEW_API_KEY", "env_key")
        key = _resolve_api_key("explicit_key")
        assert key == "explicit_key"

    def test_missing_key_raises_error(self, monkeypatch):
        """Test that missing API key raises RuntimeError."""
        monkeypatch.delenv("GOOGLE_STREETVIEW_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="API key missing"):
            _resolve_api_key()

    def test_empty_key_raises_error(self):
        """Test that empty string key raises RuntimeError."""
        with pytest.raises(RuntimeError, match="API key missing"):
            _resolve_api_key("")

    def test_whitespace_key_raises_error(self):
        """Test that whitespace-only key raises RuntimeError."""
        with pytest.raises(RuntimeError, match="API key missing"):
            _resolve_api_key("   ")


class TestCoerceBool:
    """Test suite for boolean coercion."""

    def test_true_values(self):
        """Test that various true values are coerced correctly."""
        true_values = [True, "true", "True", "TRUE", "t", "T", "1", "yes", "Yes", "y", "Y"]
        for value in true_values:
            assert _coerce_bool(value) is True, f"Failed for {value}"

    def test_false_values(self):
        """Test that various false values are coerced correctly."""
        false_values = [False, "false", "False", "FALSE", "f", "F", "0", "no", "No", "n", "N"]
        for value in false_values:
            assert _coerce_bool(value) is False, f"Failed for {value}"

    def test_none_is_false(self):
        """Test that None is coerced to False."""
        assert _coerce_bool(None) is False

    def test_invalid_value_raises_error(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="Cannot interpret"):
            _coerce_bool("maybe")


class TestCoerceCoordinate:
    """Test suite for coordinate coercion."""

    def test_tuple_passthrough(self):
        """Test that tuple coordinates are returned correctly."""
        coord = (40.7128, -74.0060)
        result = _coerce_coordinate(coord)
        assert result == (40.7128, -74.0060)
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)

    def test_list_converted(self):
        """Test that list coordinates are converted to tuple."""
        coord = [40.7128, -74.0060]
        result = _coerce_coordinate(coord)
        assert result == (40.7128, -74.0060)
        assert isinstance(result, tuple)

    def test_string_parsed(self):
        """Test that string coordinates are parsed correctly."""
        coord = "40.7128,-74.0060"
        result = _coerce_coordinate(coord)
        assert abs(result[0] - 40.7128) < 0.0001
        assert abs(result[1] - (-74.0060)) < 0.0001

    def test_string_with_spaces(self):
        """Test that string with spaces is parsed correctly."""
        coord = "40.7128, -74.0060"
        result = _coerce_coordinate(coord)
        assert abs(result[0] - 40.7128) < 0.0001
        assert abs(result[1] - (-74.0060)) < 0.0001

    def test_invalid_string_format(self):
        """Test that invalid string format raises ValueError."""
        with pytest.raises(ValueError, match="two comma-separated values"):
            _coerce_coordinate("40.7128")

    def test_wrong_length_tuple(self):
        """Test that wrong length tuple raises ValueError."""
        with pytest.raises((ValueError, TypeError)):
            _coerce_coordinate((40.7128,))


class TestCoerceFloat:
    """Test suite for float coercion."""

    def test_float_passthrough(self):
        """Test that float values pass through."""
        assert _coerce_float(3.14) == 3.14

    def test_int_converted(self):
        """Test that int values are converted to float."""
        assert _coerce_float(42) == 42.0
        assert isinstance(_coerce_float(42), float)

    def test_string_converted(self):
        """Test that string values are converted to float."""
        assert _coerce_float("3.14") == 3.14

    def test_none_uses_default(self):
        """Test that None uses the default value."""
        assert _coerce_float(None) == 0.0
        assert _coerce_float(None, 42.0) == 42.0


class TestNormaliseSize:
    """Test suite for frame size normalization."""

    def test_none_returns_default(self):
        """Test that None returns default frame size."""
        result = _normalise_size(None)
        assert result == (640, 480)

    def test_tuple_passthrough(self):
        """Test that tuple size is returned correctly."""
        result = _normalise_size((1920, 1080))
        assert result == (1920, 1080)

    def test_list_converted(self):
        """Test that list size is converted to tuple."""
        result = _normalise_size([1280, 720])
        assert result == (1280, 720)
        assert isinstance(result, tuple)

    def test_string_parsed(self):
        """Test that string size is parsed correctly."""
        result = _normalise_size("1920x1080")
        assert result == (1920, 1080)

    def test_string_case_insensitive(self):
        """Test that string parsing is case-insensitive."""
        result = _normalise_size("1920X1080")
        assert result == (1920, 1080)

    def test_invalid_string_format(self):
        """Test that invalid string format raises ValueError."""
        with pytest.raises(ValueError, match="WIDTHxHEIGHT"):
            _normalise_size("1920")


class TestUniqueCoordinates:
    """Test suite for coordinate deduplication."""

    def test_removes_exact_duplicates(self):
        """Test that exact duplicate coordinates are removed."""
        coords = [
            (40.7128, -74.0060),
            (40.7128, -74.0060),  # Duplicate
            (40.7589, -73.9851),
        ]
        result = unique(coords)
        assert len(result) == 2

    def test_rounds_to_precision(self):
        """Test that coordinates are rounded to 6 decimal places."""
        coords = [
            (40.7128001, -74.0060001),
            (40.7128002, -74.0060002),  # Should be considered duplicate
        ]
        result = unique(coords)
        assert len(result) == 1

    def test_preserves_order(self):
        """Test that order of first occurrence is preserved."""
        coords = [
            (40.0, -74.0),
            (41.0, -73.0),
            (40.0, -74.0),  # Duplicate of first
            (42.0, -72.0),
        ]
        result = unique(coords)
        assert len(result) == 3
        assert result[0] == (40.0, -74.0)
        assert result[1] == (41.0, -73.0)
        assert result[2] == (42.0, -72.0)

    def test_empty_list(self):
        """Test that empty list returns empty result."""
        result = unique([])
        assert result == []


class TestGetHeading:
    """Test suite for heading calculation."""

    def test_returns_string(self):
        """Test that heading is returned as a string."""
        start = (40.0, -74.0)
        end = (41.0, -74.0)
        heading = get_heading(start, end)
        assert isinstance(heading, str)

    def test_format_four_decimals(self):
        """Test that heading is formatted with 4 decimal places."""
        start = (40.0, -74.0)
        end = (41.0, -74.0)
        heading = get_heading(start, end)
        parts = heading.split(".")
        assert len(parts) == 2
        assert len(parts[1]) == 4

    def test_parseable_as_float(self):
        """Test that heading string can be parsed as float."""
        start = (40.0, -74.0)
        end = (41.0, -74.0)
        heading = get_heading(start, end)
        value = float(heading)
        assert 0 <= value <= 360


class TestBuildCoords:
    """Test suite for coordinate building from API payload."""

    def test_valid_payload(self):
        """Test that valid payload returns coordinates."""
        payload = {
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
        result = build_coords(payload)
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], tuple)
        assert len(result[0]) == 2

    def test_no_routes_raises_error(self):
        """Test that payload with no routes raises ValueError."""
        payload = {"status": "ZERO_RESULTS", "routes": []}
        with pytest.raises(ValueError, match="no routes"):
            build_coords(payload)

    def test_empty_route_raises_error(self):
        """Test that empty route raises ValueError."""
        payload = {"status": "OK", "routes": [{"legs": [{"steps": []}]}]}
        with pytest.raises(ValueError, match="empty route"):
            build_coords(payload)


@pytest.mark.unit
class TestFetchRouteCoordinates:
    """Test suite for route coordinate fetching."""

    def test_empty_origin_raises_error(self, mock_api_key):
        """Test that empty origin raises ValueError."""
        with pytest.raises(ValueError, match="Origin must not be empty"):
            fetch_route_coordinates("", "Los Angeles", api_key=mock_api_key)

    def test_empty_destination_raises_error(self, mock_api_key):
        """Test that empty destination raises ValueError."""
        with pytest.raises(ValueError, match="Destination must not be empty"):
            fetch_route_coordinates("New York", "", api_key=mock_api_key)

    @patch("streetview_simulator.api.requests.Session")
    def test_successful_fetch(self, mock_session_class, mock_api_key):
        """Test successful coordinate fetching."""
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
                                {"polyline": {"points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"}},
                            ]
                        }
                    ]
                }
            ],
        }
        mock_session.get.return_value = mock_response
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session_class.return_value = mock_session

        coords = fetch_route_coordinates("New York", "Boston", api_key=mock_api_key)

        assert isinstance(coords, list)
        assert len(coords) > 0

    @patch("streetview_simulator.api.requests.Session")
    def test_api_error_status(self, mock_session_class, mock_api_key):
        """Test handling of API error status."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ZERO_RESULTS", "error_message": "No route found"}
        mock_session.get.return_value = mock_response
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)
        mock_session_class.return_value = mock_session

        with pytest.raises(RuntimeError, match="No route found"):
            fetch_route_coordinates("Invalid", "Location", api_key=mock_api_key)
