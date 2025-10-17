"""Unit tests for the main entry point."""

import os
from unittest.mock import Mock, patch

import pytest

from streetview_simulator.__main__ import main, parse_args


class TestParseArgs:
    """Test suite for command-line argument parsing."""

    def test_default_values(self):
        """Test that default values are correctly set."""
        with patch("sys.argv", ["streetview_simulator"]):
            args = parse_args()
            assert args.fps == 16
            assert args.driveby is None
            assert args.max_workers == 8
            assert args.no_create_output_dir is False
            assert args.interactive is False

    def test_origin_destination(self):
        """Test parsing origin and destination arguments."""
        with patch("sys.argv", ["streetview_simulator", "--origin", "New York", "--destination", "Boston"]):
            args = parse_args()
            assert args.origin == "New York"
            assert args.destination == "Boston"

    def test_driveby_flags(self):
        """Test parsing driveby flags."""
        with patch("sys.argv", ["streetview_simulator", "--driveby"]):
            args = parse_args()
            assert args.driveby is True

        with patch("sys.argv", ["streetview_simulator", "--no-driveby"]):
            args = parse_args()
            assert args.driveby is False

    def test_object_parameters(self):
        """Test parsing object-related parameters."""
        with patch("sys.argv", [
            "streetview_simulator",
            "--object-coordinate", "40.7128,-74.0060",
            "--object-height", "0.5"
        ]):
            args = parse_args()
            assert args.object_coordinate == "40.7128,-74.0060"
            assert args.object_height == 0.5

    def test_output_parameters(self):
        """Test parsing output-related parameters."""
        with patch("sys.argv", [
            "streetview_simulator",
            "--output", "/path/to/video.mp4",
            "--output-directory", "/output/dir",
            "--output-name", "test.mp4"
        ]):
            args = parse_args()
            assert args.output == "/path/to/video.mp4"
            assert args.output_directory == "/output/dir"
            assert args.output_name == "test.mp4"

    def test_technical_parameters(self):
        """Test parsing technical parameters."""
        with patch("sys.argv", [
            "streetview_simulator",
            "--fps", "30",
            "--frame-size", "1920x1080",
            "--max-workers", "16"
        ]):
            args = parse_args()
            assert args.fps == 30
            assert args.frame_size == "1920x1080"
            assert args.max_workers == 16

    def test_other_flags(self):
        """Test parsing other flag arguments."""
        with patch("sys.argv", [
            "streetview_simulator",
            "--api-key", "test_key",
            "--no-create-output-dir",
            "--interactive"
        ]):
            args = parse_args()
            assert args.api_key == "test_key"
            assert args.no_create_output_dir is True
            assert args.interactive is True


class TestMain:
    """Test suite for the main function."""

    @patch("streetview_simulator.__main__.parse_args")
    @patch("streetview_simulator.api.construct_video")
    def test_interactive_mode(self, mock_construct, mock_parse_args):
        """Test main function in interactive mode."""
        mock_args = Mock()
        mock_args.interactive = True
        mock_args.origin = "New York"
        mock_args.destination = "Boston"
        mock_args.output = None
        mock_args.output_directory = "/output"
        mock_args.output_name = "test.mp4"
        mock_args.driveby = False
        mock_args.object_coordinate = None
        mock_args.object_height = None
        mock_args.fps = 16
        mock_args.frame_size = "640x480"
        mock_args.max_workers = 8
        mock_args.api_key = "test_key"
        mock_args.no_create_output_dir = False
        mock_parse_args.return_value = mock_args

        main()

        mock_construct.assert_called_once_with(
            origin="New York",
            destination="Boston",
            driveby=False,
            centercoord=None,
            height=None,
            output_path="/output/test.mp4",
            output_directory="/output",
            output_name="test.mp4",
            fps=16,
            frame_size="640x480",
            max_workers=8,
            api_key="test_key",
            create_output_dir=True,
        )

    @patch("streetview_simulator.__main__.parse_args")
    @patch("streetview_simulator.api.generate_drive_video")
    def test_non_interactive_mode(self, mock_generate, mock_parse_args):
        """Test main function in non-interactive mode."""
        mock_args = Mock()
        mock_args.interactive = False
        mock_args.origin = "New York"
        mock_args.destination = "Boston"
        mock_args.output = None
        mock_args.output_directory = "/output"
        mock_args.output_name = "test.mp4"
        mock_args.driveby = True
        mock_args.object_coordinate = "40.7128,-74.0060"
        mock_args.object_height = 0.5
        mock_args.fps = 30
        mock_args.frame_size = "1920x1080"
        mock_args.max_workers = 16
        mock_args.api_key = "test_key"
        mock_args.no_create_output_dir = True
        mock_parse_args.return_value = mock_args

        main()

        mock_generate.assert_called_once_with(
            origin="New York",
            destination="Boston",
            output_path=os.path.join("/output", "test.mp4"),
            driveby=True,
            centercoord="40.7128,-74.0060",
            height=0.5,
            fps=30,
            frame_size="1920x1080",
            max_workers=16,
            api_key="test_key",
            create_output_dir=False,
        )

    @patch("streetview_simulator.__main__.parse_args")
    @patch("streetview_simulator.api.generate_drive_video")
    def test_output_path_resolved(self, mock_generate, mock_parse_args):
        """Test that output path is correctly resolved when provided."""
        mock_args = Mock()
        mock_args.interactive = False
        mock_args.origin = "New York"
        mock_args.destination = "Boston"
        mock_args.output = "relative/path/video.mp4"
        mock_args.output_directory = None
        mock_args.output_name = None
        mock_args.driveby = False
        mock_args.object_coordinate = None
        mock_args.object_height = None
        mock_args.fps = 16
        mock_args.frame_size = None
        mock_args.max_workers = 8
        mock_args.api_key = None
        mock_args.no_create_output_dir = False
        mock_parse_args.return_value = mock_args

        main()

        # Check that the output path was converted to absolute path
        called_args = mock_generate.call_args[1]
        assert called_args["output_path"] == os.path.abspath("relative/path/video.mp4")

    @patch("streetview_simulator.__main__.parse_args")
    @patch("streetview_simulator.api.generate_drive_video")
    def test_default_output_path(self, mock_generate, mock_parse_args):
        """Test that default output path is used when none provided."""
        mock_args = Mock()
        mock_args.interactive = False
        mock_args.origin = "New York"
        mock_args.destination = "Boston"
        mock_args.output = None
        mock_args.output_directory = None
        mock_args.output_name = None
        mock_args.driveby = False
        mock_args.object_coordinate = None
        mock_args.object_height = None
        mock_args.fps = 16
        mock_args.frame_size = None
        mock_args.max_workers = 8
        mock_args.api_key = None
        mock_args.no_create_output_dir = False
        mock_parse_args.return_value = mock_args

        main()

        # Check that default output path is used
        called_args = mock_generate.call_args[1]
        assert called_args["output_path"] == os.path.join(".", "drive.mp4")

    @patch("streetview_simulator.__main__.parse_args")
    def test_interactive_mode_with_missing_args(self, mock_parse_args):
        """Test that interactive mode is used when origin/destination missing."""
        mock_args = Mock()
        mock_args.origin = ""
        mock_args.destination = ""
        mock_args.interactive = False
        mock_args.output = None
        mock_args.output_directory = None
        mock_args.output_name = None
        mock_args.driveby = False
        mock_args.object_coordinate = None
        mock_args.object_height = None
        mock_args.fps = 16
        mock_args.frame_size = None
        mock_args.max_workers = 8
        mock_args.api_key = None
        mock_args.no_create_output_dir = False
        mock_parse_args.return_value = mock_args

        with patch("streetview_simulator.api.construct_video") as mock_construct:
            main()
            mock_construct.assert_called_once()