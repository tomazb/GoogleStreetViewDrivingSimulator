"""Integration tests for complete workflows."""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from streetview_simulator.api import construct_video, generate_drive_video
from streetview_simulator.models import RouteData, VideoConfig


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test suite for complete end-to-end workflows."""

    @patch("streetview_simulator.api.make_video")
    @patch("streetview_simulator.api.download_streetview_images")
    @patch("streetview_simulator.api.fetch_route_coordinates")
    @patch("requests.Session")
    def test_regular_drive_workflow(self, mock_session_class, mock_fetch, mock_download, mock_video):
        """Test complete workflow for regular drive mode."""
        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock route coordinates
        mock_fetch.return_value = [
            (40.7128, -74.0060),  # New York
            (40.7589, -73.9851),  # Times Square
            (40.7614, -73.9776),  # Central Park
        ]
        
        # Mock image download
        mock_download.return_value.__enter__.return_value = [
            "/tmp/frame_000000.jpg",
            "/tmp/frame_000001.jpg",
            "/tmp/frame_000002.jpg",
        ]
        
        # Mock video creation
        mock_video.return_value = None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_drive.mp4")
            
            result = generate_drive_video(
                origin="New York",
                destination="Boston",
                output_path=output_path,
                fps=30,
                frame_size="1280x720",
                max_workers=4,
                api_key="test_key"
            )
            
            # Verify the workflow completed
            assert result == output_path
            mock_fetch.assert_called_once_with("New York", "Boston", session=mock_session, api_key="test_key")
            mock_download.assert_called_once()
            mock_video.assert_called_once()
            
            # Verify download parameters
            download_call = mock_download.call_args
            assert download_call.kwargs["driveby"] is False
            assert download_call.kwargs["centercoord"] is None
            assert download_call.kwargs["height"] == 0.0

    @patch("streetview_simulator.api.make_video")
    @patch("streetview_simulator.api.download_streetview_images")
    @patch("streetview_simulator.api.fetch_route_coordinates")
    @patch("requests.Session")
    def test_driveby_workflow(self, mock_session_class, mock_fetch, mock_download, mock_video):
        """Test complete workflow for driveby mode."""
        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock route coordinates
        mock_fetch.return_value = [
            (40.7128, -74.0060),  # New York
            (40.7589, -73.9851),  # Times Square
            (40.7614, -73.9776),  # Central Park
        ]
        
        # Mock image download
        mock_download.return_value.__enter__.return_value = [
            "/tmp/frame_000000.jpg",
            "/tmp/frame_000001.jpg",
            "/tmp/frame_000002.jpg",
        ]
        
        # Mock video creation
        mock_video.return_value = None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_driveby.mp4")
            center_coord = (40.7589, -73.9851)
            
            result = generate_drive_video(
                origin="New York",
                destination="Boston",
                output_path=output_path,
                driveby=True,
                centercoord=center_coord,
                height=0.5,
                fps=24,
                frame_size="1920x1080",
                max_workers=6,
                api_key="test_key"
            )
            
            # Verify the workflow completed
            assert result == output_path
            mock_fetch.assert_called_once()
            mock_download.assert_called_once()
            mock_video.assert_called_once()
            
            # Verify download parameters for driveby mode
            download_call = mock_download.call_args
            assert download_call.kwargs["driveby"] is True
            assert download_call.kwargs["centercoord"] == center_coord
            assert download_call.kwargs["height"] == 0.5

    @patch("streetview_simulator.api.generate_drive_video")
    def test_construct_video_workflow(self, mock_generate):
        """Test construct_video workflow with all parameters."""
        mock_generate.return_value = "/tmp/output.mp4"
        
        result = construct_video(
            origin="New York",
            destination="Boston",
            driveby=True,
            centercoord="40.7589,-73.9851",
            height=0.3,
            output_path="/tmp/output.mp4",
            fps=30,
            frame_size="1920x1080",
            max_workers=12,
            api_key="test_key",
            create_output_dir=False
        )
        
        assert result == "/tmp/output.mp4"
        
        # Verify generate was called with correct parameters
        call_args = mock_generate.call_args[1]
        assert call_args["origin"] == "New York"
        assert call_args["destination"] == "Boston"
        assert call_args["driveby"] is True
        assert call_args["centercoord"] == (40.7589, -73.9851)
        assert call_args["height"] == 0.3
        assert call_args["output_path"] == "/tmp/output.mp4"
        assert call_args["fps"] == 30
        assert call_args["frame_size"] == "1920x1080"
        assert call_args["max_workers"] == 12
        assert call_args["api_key"] == "test_key"
        assert call_args["create_output_dir"] is False

    @patch("streetview_simulator.api.generate_drive_video")
    @patch("builtins.input")
    @patch("streetview_simulator.api.save_location")
    def test_interactive_workflow(self, mock_save_loc, mock_input, mock_generate):
        """Test interactive workflow with user input."""
        # Mock user inputs
        mock_input.side_effect = [
            "Los Angeles",          # origin
            "San Francisco",        # destination
            "False",                # driveby
            "la_to_sf.mp4"          # filename
        ]
        
        # Mock directory selection
        mock_save_loc.return_value = "/tmp/videos"
        
        # Mock video generation
        mock_generate.return_value = "/tmp/videos/la_to_sf.mp4"
        
        result = construct_video(api_key="test_key")
        
        assert result == "/tmp/videos/la_to_sf.mp4"
        
        # Verify generate was called with correct parameters
        call_args = mock_generate.call_args[1]
        assert call_args["origin"] == "Los Angeles"
        assert call_args["destination"] == "San Francisco"
        assert call_args["driveby"] is False
        assert call_args["output_path"] == "/tmp/videos/la_to_sf.mp4"

    @patch("streetview_simulator.api.generate_drive_video")
    @patch("builtins.input")
    @patch("streetview_simulator.api.save_location")
    def test_interactive_driveby_workflow(self, mock_save_loc, mock_input, mock_generate):
        """Test interactive workflow with driveby mode."""
        # Mock user inputs
        mock_input.side_effect = [
            "Seattle",               # origin
            "Portland",              # destination
            "True",                  # driveby
            "47.6062,-122.3321",    # centercoord (Space Needle)
            "0.184",                 # height (184m in km)
            "seattle_driveby.mp4"    # filename
        ]
        
        # Mock directory selection
        mock_save_loc.return_value = "/tmp/videos"
        
        # Mock video generation
        mock_generate.return_value = "/tmp/videos/seattle_driveby.mp4"
        
        result = construct_video(api_key="test_key")
        
        assert result == "/tmp/videos/seattle_driveby.mp4"
        
        # Verify generate was called with driveby parameters
        call_args = mock_generate.call_args[1]
        assert call_args["driveby"] is True
        assert call_args["centercoord"] == (47.6062, -122.3321)
        assert call_args["height"] == 0.184


@pytest.mark.integration
class TestModelIntegration:
    """Test suite for model integration with API functions."""

    def test_video_config_with_api(self):
        """Test VideoConfig model integration with API parameters."""
        config = VideoConfig(
            origin="New York",
            destination="Boston",
            output_path="/tmp/test.mp4",
            fps=30,
            frame_size=(1920, 1080),
            max_workers=16,
            driveby=True,
            center_coord=(40.7589, -73.9851),
            object_height=0.5
        )
        
        # Verify all parameters are set correctly
        assert config.origin == "New York"
        assert config.destination == "Boston"
        assert config.fps == 30
        assert config.frame_size == (1920, 1080)
        assert config.max_workers == 16
        assert config.driveby is True
        assert config.center_coord == (40.7589, -73.9851)
        assert config.object_height == 0.5

    def test_route_data_distance_calculation(self):
        """Test RouteData distance calculation with real coordinates."""
        coordinates = [
            (40.7128, -74.0060),  # New York
            (40.7589, -73.9851),  # Times Square
            (40.7614, -73.9776),  # Central Park
        ]
        
        route = RouteData(
            origin="New York",
            destination="Central Park",
            coordinates=coordinates
        )
        
        # Verify route properties
        assert route.num_frames == 3
        assert route.distance_km > 0
        
        # The distance should be reasonable (approximately 2-3 km)
        assert 1.0 < route.distance_km < 5.0

    @patch("streetview_simulator.api.generate_drive_video")
    def test_workflow_with_various_parameters(self, mock_generate):
        """Test workflow with various parameter combinations."""
        mock_generate.return_value = "/tmp/output.mp4"
        
        # Test with minimal parameters
        construct_video(
            origin="A",
            destination="B",
            api_key="test_key"
        )
        
        # Verify generate was called with defaults
        call_args = mock_generate.call_args[1]
        assert call_args["fps"] == 16  # Default
        assert call_args["max_workers"] == 8  # Default
        assert call_args["driveby"] is False  # Default
        
        # Reset mock for next test
        mock_generate.reset_mock()
        
        # Test with custom parameters
        construct_video(
            origin="A",
            destination="B",
            fps=60,
            frame_size="3840x2160",  # 4K
            max_workers=32,
            api_key="test_key"
        )
        
        # Verify generate was called with custom parameters
        call_args = mock_generate.call_args[1]
        assert call_args["fps"] == 60
        assert call_args["frame_size"] == "3840x2160"
        assert call_args["max_workers"] == 32