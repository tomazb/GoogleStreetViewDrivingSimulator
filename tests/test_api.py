"""Unit tests for API functions."""

from unittest.mock import Mock, patch

import pytest

from streetview_simulator.api import (
    _coerce_bool,
    _coerce_coordinate,
    _coerce_float,
    _download_single_image,
    _ensure_extension,
    _normalise_size,
    _resolve_api_key,
    build_coords,
    construct_video,
    download_streetview_images,
    fetch_route_coordinates,
    generate_drive_video,
    get_heading,
    make_video,
    save_location,
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


@pytest.mark.unit
class TestDownloadStreetViewImages:
    """Test suite for downloading Street View images."""

    @patch("streetview_simulator.api._download_single_image")
    @patch("streetview_simulator.api.tempfile.TemporaryDirectory")
    @patch("streetview_simulator.api.concurrent.futures.ThreadPoolExecutor")
    def test_successful_download(self, mock_executor, mock_temp_dir, mock_download, sample_coordinates):
        """Test successful image download."""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/test"
        mock_download.return_value = (0, "/tmp/test/000000.jpg")
        
        mock_future = Mock()
        mock_future.result.return_value = (0, "/tmp/test/000000.jpg")
        mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

        with download_streetview_images(sample_coordinates, api_key="test_key") as images:
            assert len(images) == len(sample_coordinates)
            assert all(path.endswith(".jpg") for path in images)

    def test_empty_coordinates(self):
        """Test that empty coordinates raises ValueError."""
        with pytest.raises(ValueError, match="No coordinates provided"):
            with download_streetview_images([], api_key="test_key"):
                pass

    def test_driveby_without_centercoord(self, sample_coordinates):
        """Test that driveby=True without centercoord raises ValueError."""
        with pytest.raises(ValueError, match="centercoord is required when driveby is True"):
            with download_streetview_images(sample_coordinates, driveby=True, api_key="test_key"):
                pass

    @patch("streetview_simulator.api._download_single_image")
    @patch("streetview_simulator.api.tempfile.TemporaryDirectory")
    @patch("streetview_simulator.api.concurrent.futures.ThreadPoolExecutor")
    def test_driveby_mode(self, mock_executor, mock_temp_dir, mock_download, sample_coordinates):
        """Test driveby mode with center coordinate."""
        # Setup mocks
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/test"
        mock_download.return_value = (0, "/tmp/test/000000.jpg")
        
        mock_future = Mock()
        mock_future.result.return_value = (0, "/tmp/test/000000.jpg")
        mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

        center_coord = (40.7589, -73.9851)
        with download_streetview_images(
            sample_coordinates,
            driveby=True,
            centercoord=center_coord,
            height=0.5,
            api_key="test_key"
        ) as images:
            assert len(images) == len(sample_coordinates)


@pytest.mark.unit
class TestMakeVideo:
    """Test suite for video creation."""

    @patch("cv2.imread")
    @patch("cv2.VideoWriter")
    @patch("cv2.VideoWriter_fourcc")
    def test_successful_video_creation(self, mock_fourcc, mock_writer, mock_imread, temp_output_dir):
        """Test successful video creation."""
        # Setup mocks
        mock_imread.return_value = Mock(shape=(480, 640, 3))
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        mock_writer_instance.isOpened.return_value = True
        mock_fourcc.return_value = "mp4v"

        # Create test image paths
        image_paths = [
            str(temp_output_dir / "frame1.jpg"),
            str(temp_output_dir / "frame2.jpg"),
        ]

        output_path = str(temp_output_dir / "output.mp4")
        make_video(image_paths, output_path)

        # Verify that writer was called correctly
        mock_writer.assert_called_once()
        mock_writer_instance.write.assert_called()

    def test_empty_images(self, temp_output_dir):
        """Test that empty image list raises ValueError."""
        output_path = str(temp_output_dir / "output.mp4")
        with pytest.raises(ValueError, match="No images provided"):
            make_video([], output_path)

    @patch("cv2.imread")
    def test_unreadable_first_frame(self, mock_imread, temp_output_dir):
        """Test handling of unreadable first frame."""
        mock_imread.return_value = None
        
        image_paths = [str(temp_output_dir / "frame1.jpg")]
        output_path = str(temp_output_dir / "output.mp4")
        
        with pytest.raises(RuntimeError, match="Unable to load frame"):
            make_video(image_paths, output_path)

    @patch("cv2.imread")
    @patch("cv2.VideoWriter")
    @patch("cv2.VideoWriter_fourcc")
    def test_unreadable_subsequent_frame(self, mock_fourcc, mock_writer, mock_imread, temp_output_dir):
        """Test handling of unreadable subsequent frames."""
        # First frame loads successfully, subsequent frames fail
        mock_imread.side_effect = [Mock(shape=(480, 640, 3)), None]
        
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        mock_writer_instance.isOpened.return_value = True
        mock_fourcc.return_value = "mp4v"

        image_paths = [
            str(temp_output_dir / "frame1.jpg"),
            str(temp_output_dir / "frame2.jpg"),
        ]
        output_path = str(temp_output_dir / "output.mp4")
        
        with pytest.raises(RuntimeError, match="Unable to load frame"):
            make_video(image_paths, output_path)

    @patch("cv2.imread")
    @patch("cv2.VideoWriter")
    @patch("cv2.VideoWriter_fourcc")
    def test_writer_not_opened(self, mock_fourcc, mock_writer, mock_imread, temp_output_dir):
        """Test handling when video writer cannot be opened."""
        mock_imread.return_value = Mock(shape=(480, 640, 3))
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        mock_writer_instance.isOpened.return_value = False
        mock_fourcc.return_value = "mp4v"

        image_paths = [str(temp_output_dir / "frame1.jpg")]
        output_path = str(temp_output_dir / "output.mp4")
        
        with pytest.raises(RuntimeError, match="Unable to open video writer"):
            make_video(image_paths, output_path)


@pytest.mark.unit
class TestGenerateDriveVideo:
    """Test suite for generate_drive_video function."""

    @patch("streetview_simulator.api.make_video")
    @patch("streetview_simulator.api.download_streetview_images")
    @patch("streetview_simulator.api.fetch_route_coordinates")
    @patch("requests.Session")
    def test_successful_generation(self, mock_session_class, mock_fetch, mock_download, mock_video, temp_output_dir):
        """Test successful video generation."""
        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_fetch.return_value = [(40.7128, -74.0060), (40.7589, -73.9851)]
        
        mock_download.return_value.__enter__.return_value = [
            str(temp_output_dir / "frame1.jpg"),
            str(temp_output_dir / "frame2.jpg"),
        ]
        
        output_path = str(temp_output_dir / "output.mp4")
        result = generate_drive_video(
            origin="New York",
            destination="Boston",
            output_path=output_path,
            api_key="test_key"
        )
        
        assert result == output_path
        mock_fetch.assert_called_once()
        mock_download.assert_called_once()
        mock_video.assert_called_once()

    @patch("requests.Session")
    def test_driveby_mode(self, mock_session_class, temp_output_dir):
        """Test generate_drive_video in driveby mode."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        output_path = str(temp_output_dir / "output.mp4")
        
        with patch("streetview_simulator.api.fetch_route_coordinates") as mock_fetch, \
             patch("streetview_simulator.api.download_streetview_images") as mock_download, \
             patch("streetview_simulator.api.make_video") as mock_video:
            
            mock_fetch.return_value = [(40.7128, -74.0060), (40.7589, -73.9851)]
            mock_download.return_value.__enter__.return_value = [
                str(temp_output_dir / "frame1.jpg"),
                str(temp_output_dir / "frame2.jpg"),
            ]
            
            generate_drive_video(
                origin="New York",
                destination="Boston",
                output_path=output_path,
                driveby=True,
                centercoord=(40.7589, -73.9851),
                height=0.5,
                api_key="test_key"
            )
            
            # Verify download was called with driveby parameters
            mock_download.assert_called_once()
            call_args = mock_download.call_args
            assert call_args.kwargs["driveby"] is True
            assert call_args.kwargs["centercoord"] == (40.7589, -73.9851)
            assert call_args.kwargs["height"] == 0.5


@pytest.mark.unit
class TestConstructVideo:
    """Test suite for construct_video function."""

    @patch("streetview_simulator.api.generate_drive_video")
    def test_non_interactive_mode(self, mock_generate):
        """Test construct_video in non-interactive mode."""
        mock_generate.return_value = "/tmp/output.mp4"
        
        result = construct_video(
            origin="New York",
            destination="Boston",
            output_path="/tmp/output.mp4",
            api_key="test_key"
        )
        
        assert result == "/tmp/output.mp4"
        mock_generate.assert_called_once()

    @patch("streetview_simulator.api.generate_drive_video")
    @patch("builtins.input")
    def test_interactive_mode(self, mock_input, mock_generate):
        """Test construct_video in interactive mode."""
        # Mock user input
        mock_input.side_effect = [
            "New York",  # origin
            "Boston",    # destination
            "False",     # driveby
            "test.mp4"   # filename
        ]
        
        mock_generate.return_value = "/tmp/test.mp4"
        
        with patch("streetview_simulator.api.save_location") as mock_save_loc:
            mock_save_loc.return_value = "/tmp"
            
            result = construct_video(api_key="test_key")
            
            assert result == "/tmp/test.mp4"
            mock_generate.assert_called_once()

    @patch("streetview_simulator.api.generate_drive_video")
    @patch("builtins.input")
    def test_interactive_driveby_mode(self, mock_input, mock_generate):
        """Test construct_video in interactive driveby mode."""
        # Mock user input
        mock_input.side_effect = [
            "New York",              # origin
            "Boston",                # destination
            "True",                  # driveby
            "40.7589,-73.9851",      # centercoord
            "0.5",                   # height
            "test_driveby.mp4"       # filename
        ]
        
        mock_generate.return_value = "/tmp/test_driveby.mp4"
        
        with patch("streetview_simulator.api.save_location") as mock_save_loc:
            mock_save_loc.return_value = "/tmp"
            
            result = construct_video(api_key="test_key")
            
            assert result == "/tmp/test_driveby.mp4"
            
            # Verify generate was called with driveby parameters
            call_args = mock_generate.call_args[1]
            assert call_args["driveby"] is True
            assert call_args["centercoord"] == (40.7589, -73.9851)
            assert call_args["height"] == 0.5

    @patch("streetview_simulator.api.generate_drive_video")
    @patch("builtins.input")
    def test_output_path_with_extension(self, mock_input, mock_generate):
        """Test that output path extension is handled correctly."""
        mock_generate.return_value = "/tmp/test.mp4"
        
        result = construct_video(
            origin="New York",
            destination="Boston",
            output_path="/tmp/test",  # No extension
            api_key="test_key"
        )
        
        assert result == "/tmp/test.mp4"
        
        # Verify generate was called with correct path
        call_args = mock_generate.call_args[1]
        assert call_args["output_path"] == "/tmp/test.mp4"


@pytest.mark.unit
class TestSaveLocation:
    """Test suite for save_location function."""

    @patch("builtins.input")
    @patch("os.path.isdir")
    def test_existing_directory(self, mock_isdir, mock_input):
        """Test returning an existing directory."""
        mock_input.return_value = "/existing/path"
        mock_isdir.return_value = True
        
        result = save_location()
        assert result == "/existing/path"

    @patch("builtins.input")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    def test_create_new_directory(self, mock_makedirs, mock_isdir, mock_input):
        """Test creating a new directory."""
        mock_input.return_value = "/new/path"
        mock_isdir.return_value = False
        
        result = save_location(create_missing=True)
        assert result == "/new/path"
        mock_makedirs.assert_called_once_with("/new/path", exist_ok=True)

    @patch("builtins.input")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("builtins.print")
    def test_directory_creation_failure(self, mock_print, mock_makedirs, mock_isdir, mock_input):
        """Test handling directory creation failure."""
        mock_input.side_effect = ["/fail/path", "/existing/path"]
        mock_isdir.side_effect = [False, True]
        mock_makedirs.side_effect = OSError("Permission denied")
        
        result = save_location(create_missing=True)
        assert result == "/existing/path"
        mock_print.assert_called_with("Unable to create directory /fail/path: Permission denied")

    @patch("builtins.input")
    @patch("os.path.isdir")
    @patch("builtins.print")
    def test_invalid_path_no_create(self, mock_print, mock_isdir, mock_input):
        """Test invalid path when not creating directories."""
        mock_input.side_effect = ["", "/invalid/path", "/existing/path"]
        mock_isdir.side_effect = [False, False, True]
        
        result = save_location(create_missing=False)
        assert result == "/existing/path"
        mock_print.assert_any_call("Path must not be empty.")
        mock_print.assert_any_call("Invalid path: /invalid/path")

    @patch("builtins.input")
    @patch("os.path.isdir")
    @patch("builtins.print")
    def test_empty_path_retry(self, mock_print, mock_isdir, mock_input):
        """Test retry when empty path is provided."""
        mock_input.side_effect = ["", "", "/valid/path"]
        mock_isdir.side_effect = [False, False, True]
        
        result = save_location()
        assert result == "/valid/path"
        assert mock_print.call_count == 2  # Two empty path warnings


@pytest.mark.unit
class TestEnsureExtension:
    """Test suite for _ensure_extension function."""

    def test_with_extension(self):
        """Test filename with existing extension."""
        result = _ensure_extension("video.mp4", ".avi")
        assert result == "video.mp4"

    def test_without_extension(self):
        """Test filename without extension."""
        result = _ensure_extension("video", ".mp4")
        assert result == "video.mp4"

    def test_empty_filename(self):
        """Test empty filename raises ValueError."""
        with pytest.raises(ValueError, match="File name must not be empty"):
            _ensure_extension("", ".mp4")

    def test_whitespace_filename(self):
        """Test whitespace-only filename raises ValueError."""
        with pytest.raises(ValueError, match="File name must not be empty"):
            _ensure_extension("   ", ".mp4")

    def test_filename_with_dot(self):
        """Test filename with dot but no extension."""
        result = _ensure_extension("video.", ".mp4")
        assert result == "video..mp4"

    def test_filename_with_spaces(self):
        """Test filename with spaces."""
        result = _ensure_extension("  my video  ", ".mp4")
        assert result == "  my video  .mp4"


@pytest.mark.unit
class TestDownloadSingleImage:
    """Test suite for _download_single_image function."""

    @patch("time.sleep")
    @patch("os.path.exists")
    @patch("os.remove")
    @patch("builtins.open")
    @patch("requests.Session.get")
    def test_successful_download(self, mock_get, mock_open, mock_remove, mock_exists, mock_sleep):
        """Test successful image download."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/jpeg"}
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.iter_content.return_value = [b"image_data"]
        mock_get.return_value = mock_response
        
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_open.return_value.__exit__.return_value = None
        
        mock_exists.return_value = False
        
        session = Mock()
        params = {"key": "test", "location": "40.7128,-74.0060"}
        
        result = _download_single_image(session, params, "/tmp", 0)
        
        assert result == (0, "/tmp/000000.jpg")
        mock_get.assert_called_once()
        mock_open.assert_called_once_with("/tmp/000000.jpg", "wb")
        mock_file.write.assert_called_once_with(b"image_data")

    @patch("time.sleep")
    @patch("os.path.exists")
    @patch("os.remove")
    @patch("requests.Session.get")
    def test_retry_on_failure(self, mock_get, mock_remove, mock_exists, mock_sleep):
        """Test retry mechanism on download failure."""
        # Setup mocks for failure then success
        mock_fail_response = Mock()
        mock_fail_response.status_code = 500
        mock_fail_response.headers = {"Content-Type": "text/html"}
        mock_fail_response.text = "Internal Server Error"
        mock_fail_response.__enter__.return_value = mock_fail_response
        mock_fail_response.__exit__.return_value = None
        
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.headers = {"Content-Type": "image/jpeg"}
        mock_success_response.__enter__.return_value = mock_success_response
        mock_success_response.__exit__.return_value = None
        mock_success_response.iter_content.return_value = [b"image_data"]
        
        mock_get.side_effect = [mock_fail_response, mock_success_response]
        mock_exists.return_value = False
        
        with patch("builtins.open") as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_open.return_value.__exit__.return_value = None
            
            session = Mock()
            params = {"key": "test", "location": "40.7128,-74.0060"}
            
            result = _download_single_image(session, params, "/tmp", 0)
            
            assert result == (0, "/tmp/000000.jpg")
            assert mock_get.call_count == 2
            mock_sleep.assert_called_once()

    @patch("time.sleep")
    @patch("os.path.exists")
    @patch("os.remove")
    @patch("requests.Session.get")
    def test_max_retries_exceeded(self, mock_get, mock_remove, mock_exists, mock_sleep):
        """Test failure after maximum retries."""
        # Setup mocks for consistent failure
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "Internal Server Error"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_get.return_value = mock_response
        
        mock_exists.return_value = False
        
        session = Mock()
        params = {"key": "test", "location": "40.7128,-74.0060"}
        
        with pytest.raises(RuntimeError, match="Street View API request failed after 4 attempts"):
            _download_single_image(session, params, "/tmp", 0)
        
        assert mock_get.call_count == 4
        assert mock_sleep.call_count == 3
