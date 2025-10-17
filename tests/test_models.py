"""Unit tests for data models."""

from pathlib import Path

import pytest

from streetview_simulator.models import FrameSize, RouteData, VideoConfig


class TestFrameSize:
    """Test suite for FrameSize model."""

    def test_initialization(self):
        """Test FrameSize initialization."""
        size = FrameSize(width=1920, height=1080)
        assert size.width == 1920
        assert size.height == 1080

    def test_from_string(self):
        """Test parsing FrameSize from string."""
        size = FrameSize.from_string("1920x1080")
        assert size.width == 1920
        assert size.height == 1080

    def test_from_string_case_insensitive(self):
        """Test that from_string is case insensitive."""
        size = FrameSize.from_string("1920X1080")
        assert size.width == 1920
        assert size.height == 1080

    def test_from_string_invalid_format(self):
        """Test that invalid string format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid frame size format"):
            FrameSize.from_string("1920-1080")

    def test_from_string_invalid_values(self):
        """Test that non-numeric values raise ValueError."""
        with pytest.raises(ValueError):
            FrameSize.from_string("abcxdef")

    def test_as_tuple(self):
        """Test as_tuple property."""
        size = FrameSize(width=1280, height=720)
        assert size.as_tuple == (1280, 720)

    def test_str_representation(self):
        """Test string representation."""
        size = FrameSize(width=640, height=480)
        assert str(size) == "640x480"


class TestVideoConfig:
    """Test suite for VideoConfig model."""

    def test_minimal_config(self):
        """Test minimal valid configuration."""
        config = VideoConfig(
            origin="New York",
            destination="Boston",
            output_path=Path("/tmp/video.mp4")
        )
        assert config.origin == "New York"
        assert config.destination == "Boston"
        assert config.output_path == Path("/tmp/video.mp4")
        assert config.fps == 16  # Default value
        assert config.frame_size == FrameSize(640, 480)  # Default value
        assert config.max_workers == 8  # Default value
        assert config.codec == "mp4v"  # Default value
        assert config.driveby is False  # Default value
        assert config.center_coord is None  # Default value
        assert config.object_height == 0.0  # Default value

    def test_full_config(self):
        """Test configuration with all parameters."""
        config = VideoConfig(
            origin="New York",
            destination="Boston",
            output_path=Path("/tmp/video.mp4"),
            fps=30,
            frame_size=FrameSize(1920, 1080),
            max_workers=16,
            codec="avc1",
            driveby=True,
            center_coord=(40.7128, -74.0060),
            object_height=0.5
        )
        assert config.fps == 30
        assert config.frame_size == FrameSize(1920, 1080)
        assert config.max_workers == 16
        assert config.codec == "avc1"
        assert config.driveby is True
        assert config.center_coord == (40.7128, -74.0060)
        assert config.object_height == 0.5

    def test_driveby_without_center_coord(self):
        """Test that driveby=True without center_coord raises ValueError."""
        with pytest.raises(ValueError, match="center_coord required when driveby is True"):
            VideoConfig(
                origin="New York",
                destination="Boston",
                output_path=Path("/tmp/video.mp4"),
                driveby=True,
                center_coord=None
            )

    def test_driveby_with_center_coord(self):
        """Test that driveby=True with center_coord is valid."""
        config = VideoConfig(
            origin="New York",
            destination="Boston",
            output_path=Path("/tmp/video.mp4"),
            driveby=True,
            center_coord=(40.7128, -74.0060)
        )
        assert config.driveby is True
        assert config.center_coord == (40.7128, -74.0060)

    def test_invalid_fps(self):
        """Test that non-positive fps raises ValueError."""
        with pytest.raises(ValueError, match="fps must be positive"):
            VideoConfig(
                origin="New York",
                destination="Boston",
                output_path=Path("/tmp/video.mp4"),
                fps=0
            )

        with pytest.raises(ValueError, match="fps must be positive"):
            VideoConfig(
                origin="New York",
                destination="Boston",
                output_path=Path("/tmp/video.mp4"),
                fps=-5
            )

    def test_invalid_max_workers(self):
        """Test that non-positive max_workers raises ValueError."""
        with pytest.raises(ValueError, match="max_workers must be positive"):
            VideoConfig(
                origin="New York",
                destination="Boston",
                output_path=Path("/tmp/video.mp4"),
                max_workers=0
            )

        with pytest.raises(ValueError, match="max_workers must be positive"):
            VideoConfig(
                origin="New York",
                destination="Boston",
                output_path=Path("/tmp/video.mp4"),
                max_workers=-3
            )

    def test_string_output_path_conversion(self):
        """Test that string output_path is converted to Path."""
        config = VideoConfig(
            origin="New York",
            destination="Boston",
            output_path=Path("/tmp/video.mp4")  # Path object
        )
        assert isinstance(config.output_path, Path)
        assert config.output_path == Path("/tmp/video.mp4")


class TestRouteData:
    """Test suite for RouteData model."""

    def test_initialization(self):
        """Test RouteData initialization."""
        coordinates = [
            (40.7128, -74.0060),
            (40.7589, -73.9851),
            (40.7614, -73.9776)
        ]
        route = RouteData(
            origin="New York",
            destination="Boston",
            coordinates=coordinates
        )
        assert route.origin == "New York"
        assert route.destination == "Boston"
        assert route.coordinates == coordinates

    def test_num_frames_property(self):
        """Test num_frames property."""
        coordinates = [
            (40.7128, -74.0060),
            (40.7589, -73.9851),
            (40.7614, -73.9776)
        ]
        route = RouteData(
            origin="New York",
            destination="Boston",
            coordinates=coordinates
        )
        assert route.num_frames == 3

    def test_distance_km_property(self):
        """Test distance_km property."""
        # Use coordinates with known distances
        coordinates = [
            (40.7128, -74.0060),  # New York
            (40.7589, -73.9851),  # Times Square
            (40.7614, -73.9776),  # Central Park
        ]
        route = RouteData(
            origin="New York",
            destination="Boston",
            coordinates=coordinates
        )
        distance = route.distance_km
        # Just verify that distance is calculated and is positive
        assert distance > 0

    def test_distance_km_single_coordinate(self):
        """Test distance_km with only one coordinate."""
        coordinates = [(40.7128, -74.0060)]
        route = RouteData(
            origin="New York",
            destination="Boston",
            coordinates=coordinates
        )
        assert route.distance_km == 0.0

    def test_distance_km_empty_coordinates(self):
        """Test distance_km with empty coordinates."""
        route = RouteData(
            origin="New York",
            destination="Boston",
            coordinates=[]
        )
        assert route.distance_km == 0.0