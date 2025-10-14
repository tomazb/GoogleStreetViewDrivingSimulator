"""Mathematical calculations for geographic coordinates and bearings."""

import math

Coordinate = tuple[float, float]


def calculate_initial_compass_bearing(point_a: Coordinate, point_b: Coordinate) -> float:
    """
    Calculate the bearing between two geographic points.

    Uses the formula:
        θ = atan2(sin(Δlong)·cos(lat2),
                  cos(lat1)·sin(lat2) − sin(lat1)·cos(lat2)·cos(Δlong))

    Based on implementation by jeromer: https://gist.github.com/jeromer/2005586

    Args:
        point_a: Tuple of (latitude, longitude) in decimal degrees for the first point
        point_b: Tuple of (latitude, longitude) in decimal degrees for the second point

    Returns:
        The bearing in degrees (0-360), where 0/360 is North

    Raises:
        TypeError: If points are not tuples
        ValueError: If coordinates are invalid

    Example:
        >>> calculate_initial_compass_bearing((40.7128, -74.0060), (51.5074, -0.1278))
        51.47
    """
    if not isinstance(point_a, tuple) or not isinstance(point_b, tuple):
        msg = "Only tuples are supported as arguments"
        raise TypeError(msg)

    if len(point_a) != 2 or len(point_b) != 2:
        msg = "Coordinates must be tuples of (latitude, longitude)"
        raise ValueError(msg)

    lat1 = math.radians(point_a[0])
    lat2 = math.radians(point_b[0])
    diff_long = math.radians(point_b[1] - point_a[1])

    x = math.sin(diff_long) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_long))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    return (initial_bearing + 360) % 360



def calculate_distance(origin: Coordinate, destination: Coordinate) -> float:
    """
    Calculate the distance between two points using the Haversine formula.

    Based on implementation by Wayne Dyck.

    Args:
        origin: Tuple of (latitude, longitude) in decimal degrees
        destination: Tuple of (latitude, longitude) in decimal degrees

    Returns:
        Distance in kilometers

    Example:
        >>> calculate_distance((40.7128, -74.0060), (34.0522, -118.2437))
        3935.75
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c



def calculate_pitch(center_coord: Coordinate, current_coord: Coordinate, height: float) -> str:
    """
    Calculate the pitch angle to look at an object from a given position.

    Args:
        center_coord: Coordinate of the object being viewed
        current_coord: Current camera position coordinate
        height: Height of the object in kilometers

    Returns:
        Pitch angle as a formatted string with 4 decimal places

    Example:
        >>> calculate_pitch((40.7128, -74.0060), (40.7120, -74.0070), 0.3)
        '19.4712'
    """
    distance = calculate_distance(center_coord, current_coord)
    if distance == 0:
        return "0.0000"

    pitch_radians = math.atan(height / distance)
    pitch_degrees = math.degrees(pitch_radians)

    return f"{pitch_degrees:.4f}"
