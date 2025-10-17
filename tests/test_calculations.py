"""Unit tests for calculation functions."""

import pytest

from streetview_simulator.calculations import calculate_distance, calculate_initial_compass_bearing, calculate_pitch


class TestCalculateInitialCompassBearing:
    """Test suite for bearing calculations."""

    def test_north_bearing(self):
        """Test bearing calculation for northward direction."""
        point_a = (40.0, -74.0)
        point_b = (41.0, -74.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        # Should be close to 0 (North) or 360
        assert 359.0 < bearing < 361.0 or -1.0 < bearing < 1.0

    def test_east_bearing(self):
        """Test bearing calculation for eastward direction."""
        point_a = (40.0, -74.0)
        point_b = (40.0, -73.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        # Should be close to 90 (East)
        assert 89.0 < bearing < 91.0

    def test_south_bearing(self):
        """Test bearing calculation for southward direction."""
        point_a = (41.0, -74.0)
        point_b = (40.0, -74.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        # Should be close to 180 (South)
        assert 179.0 < bearing < 181.0

    def test_west_bearing(self):
        """Test bearing calculation for westward direction."""
        point_a = (40.0, -73.0)
        point_b = (40.0, -74.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        # Should be close to 270 (West)
        assert 269.0 < bearing < 271.0

    def test_invalid_input_not_tuple(self):
        """Test that non-tuple inputs raise TypeError."""
        with pytest.raises(TypeError, match="Only tuples are supported"):
            calculate_initial_compass_bearing([40.0, -74.0], (41.0, -74.0))

    def test_invalid_coordinate_length(self):
        """Test that invalid coordinate tuples raise ValueError."""
        with pytest.raises(ValueError, match="must be tuples"):
            calculate_initial_compass_bearing((40.0,), (41.0, -74.0))

    def test_same_point(self):
        """Test bearing calculation when start and end are the same."""
        point = (40.7128, -74.0060)
        bearing = calculate_initial_compass_bearing(point, point)
        # Bearing should be 0 (or very close due to floating point)
        assert abs(bearing) < 0.01 or abs(bearing - 360) < 0.01

    def test_return_type(self):
        """Test that bearing is returned as a float."""
        point_a = (40.0, -74.0)
        point_b = (41.0, -74.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        assert isinstance(bearing, float)

    def test_bearing_range(self):
        """Test that bearing is always in range 0-360."""
        test_cases = [
            ((0, 0), (1, 1)),
            ((51.5074, -0.1278), (40.7128, -74.0060)),  # London to NYC
            ((-33.8688, 151.2093), (35.6762, 139.6503)),  # Sydney to Tokyo
        ]
        for point_a, point_b in test_cases:
            bearing = calculate_initial_compass_bearing(point_a, point_b)
            assert 0 <= bearing <= 360, f"Bearing {bearing} out of range for {point_a} -> {point_b}"


class TestCalculateDistance:
    """Test suite for distance calculations."""

    def test_same_point_distance(self):
        """Test that distance from a point to itself is zero."""
        point = (40.7128, -74.0060)
        distance = calculate_distance(point, point)
        assert distance == 0.0

    def test_known_distance_ny_la(self):
        """Test distance calculation with known values (NY to LA)."""
        ny = (40.7128, -74.0060)
        la = (34.0522, -118.2437)
        distance = calculate_distance(ny, la)
        # Expected ~3935 km (approximate)
        assert 3900 < distance < 4000

    def test_known_distance_london_paris(self):
        """Test distance calculation (London to Paris)."""
        london = (51.5074, -0.1278)
        paris = (48.8566, 2.3522)
        distance = calculate_distance(london, paris)
        # Expected ~344 km
        assert 340 < distance < 350

    def test_symmetry(self):
        """Test that distance(A, B) == distance(B, A)."""
        point_a = (40.7128, -74.0060)
        point_b = (34.0522, -118.2437)
        dist_ab = calculate_distance(point_a, point_b)
        dist_ba = calculate_distance(point_b, point_a)
        assert abs(dist_ab - dist_ba) < 0.01  # Should be essentially equal

    def test_return_type(self):
        """Test that distance is returned as a float."""
        point_a = (40.0, -74.0)
        point_b = (41.0, -74.0)
        distance = calculate_distance(point_a, point_b)
        assert isinstance(distance, float)

    def test_positive_distance(self):
        """Test that distance is always positive."""
        test_cases = [
            ((0, 0), (1, 1)),
            ((51.5074, -0.1278), (40.7128, -74.0060)),
            ((-33.8688, 151.2093), (35.6762, 139.6503)),
        ]
        for point_a, point_b in test_cases:
            distance = calculate_distance(point_a, point_b)
            assert distance >= 0, f"Distance {distance} is negative for {point_a} -> {point_b}"

    def test_small_distance(self):
        """Test distance calculation for very close points."""
        point_a = (40.7128, -74.0060)
        point_b = (40.7129, -74.0061)  # Very close
        distance = calculate_distance(point_a, point_b)
        # Should be less than 1 km
        assert 0 < distance < 1


class TestCalculatePitch:
    """Test suite for pitch angle calculations."""

    def test_zero_distance(self):
        """Test pitch when at the object location."""
        coord = (40.7128, -74.0060)
        pitch = calculate_pitch(coord, coord, 0.5)
        assert pitch == "0.0000"

    def test_pitch_format(self):
        """Test that pitch is formatted with 4 decimal places."""
        center = (40.7128, -74.0060)
        current = (40.7120, -74.0070)
        pitch = calculate_pitch(center, current, 0.3)
        assert "." in pitch
        decimals = pitch.split(".")[1]
        assert len(decimals) == 4

    def test_increasing_height(self):
        """Test that pitch increases with object height."""
        center = (40.7128, -74.0060)
        current = (40.7100, -74.0100)
        pitch_low = float(calculate_pitch(center, current, 0.1))
        pitch_high = float(calculate_pitch(center, current, 0.5))
        assert pitch_high > pitch_low

    def test_increasing_distance(self):
        """Test that pitch decreases as you move away from object."""
        center = (40.7128, -74.0060)
        close = (40.7120, -74.0070)
        far = (40.7100, -74.0100)
        height = 0.3
        pitch_close = float(calculate_pitch(center, close, height))
        pitch_far = float(calculate_pitch(center, far, height))
        assert pitch_close > pitch_far

    def test_zero_height(self):
        """Test pitch with zero height."""
        center = (40.7128, -74.0060)
        current = (40.7100, -74.0100)
        pitch = float(calculate_pitch(center, current, 0.0))
        assert pitch == 0.0

    def test_return_type(self):
        """Test that pitch is returned as a string."""
        center = (40.7128, -74.0060)
        current = (40.7120, -74.0070)
        pitch = calculate_pitch(center, current, 0.3)
        assert isinstance(pitch, str)

    def test_pitch_positive(self):
        """Test that pitch is always positive (looking up)."""
        test_cases = [
            ((40.0, -74.0), (41.0, -74.0), 0.5),
            ((0, 0), (1, 1), 0.3),
            ((51.5074, -0.1278), (40.7128, -74.0060), 1.0),
        ]
        for center, current, height in test_cases:
            pitch = float(calculate_pitch(center, current, height))
            assert pitch >= 0, f"Pitch {pitch} is negative for {center} -> {current} with height {height}"

    def test_pitch_reasonable_range(self):
        """Test that pitch angles are in a reasonable range (0-90 degrees)."""
        center = (40.7128, -74.0060)
        current = (40.7100, -74.0100)
        height = 0.5  # 500 meters
        pitch = float(calculate_pitch(center, current, height))
        # Pitch should be between 0 and 90 degrees
        assert 0 <= pitch <= 90, f"Pitch {pitch} out of reasonable range"


class TestCalculationIntegration:
    """Test suite for integration between calculation functions."""

    def test_bearing_and_pitch_together(self):
        """Test bearing and pitch calculations work together."""
        center = (40.7128, -74.0060)
        current = (40.7100, -74.0100)
        height = 0.3
        
        # Calculate bearing from current to next point
        next_point = (40.7150, -74.0050)
        bearing = calculate_initial_compass_bearing(current, next_point)
        
        # Calculate pitch for object at center
        pitch = calculate_pitch(center, current, height)
        
        # Both should be valid values
        assert 0 <= bearing <= 360
        assert pitch is not None
        assert float(pitch) >= 0

    def test_distance_calculation_with_bearing(self):
        """Test distance calculation with bearing for route planning."""
        points = [
            (40.7128, -74.0060),  # Start
            (40.7138, -74.0050),  # Point 1
            (40.7148, -74.0040),  # Point 2
        ]
        
        # Calculate distances between consecutive points
        distances = []
        bearings = []
        
        for i in range(len(points) - 1):
            dist = calculate_distance(points[i], points[i + 1])
            bear = calculate_initial_compass_bearing(points[i], points[i + 1])
            distances.append(dist)
            bearings.append(bear)
        
        # All distances should be positive
        assert all(d > 0 for d in distances)
        
        # All bearings should be valid
        assert all(0 <= b <= 360 for b in bearings)
        
        # Total distance should be sum of individual distances
        total_distance = sum(distances)
        direct_distance = calculate_distance(points[0], points[-1])
        
        # Total distance should be greater than or equal to direct distance
        assert total_distance >= direct_distance

    def test_pitch_calculation_edge_cases(self):
        """Test pitch calculation with various edge cases."""
        center = (40.7128, -74.0060)
        
        # Test with very close coordinates
        close = (40.7128, -74.0061)  # Very close
        pitch = calculate_pitch(center, close, 0.1)
        assert float(pitch) >= 0
        
        # Test with very tall object
        tall = (40.7100, -74.0100)  # Far away
        pitch = calculate_pitch(center, tall, 1.0)  # 1km tall
        assert float(pitch) >= 0
        
        # Test with very short object
        short = (40.7100, -74.0100)  # Far away
        pitch = calculate_pitch(center, short, 0.001)  # 1m tall
        assert float(pitch) >= 0

    def test_bearing_calculation_with_cardinal_directions(self):
        """Test bearing calculation with known cardinal directions."""
        # Test north
        start = (40.0, -74.0)
        end = (41.0, -74.0)  # Directly north
        bearing = calculate_initial_compass_bearing(start, end)
        assert 359 <= bearing <= 360 or 0 <= bearing <= 1  # Allow for floating point
        
        # Test east
        start = (40.0, -74.0)
        end = (40.0, -73.0)  # Directly east
        bearing = calculate_initial_compass_bearing(start, end)
        assert 89 <= bearing <= 91
        
        # Test south
        start = (41.0, -74.0)
        end = (40.0, -74.0)  # Directly south
        bearing = calculate_initial_compass_bearing(start, end)
        assert 179 <= bearing <= 181
        
        # Test west
        start = (40.0, -73.0)
        end = (40.0, -74.0)  # Directly west
        bearing = calculate_initial_compass_bearing(start, end)
        assert 269 <= bearing <= 271
