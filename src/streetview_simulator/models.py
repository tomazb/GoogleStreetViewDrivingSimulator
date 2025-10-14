"""Data models for the Street View Simulator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


Coordinate = tuple[float, float]


@dataclass(frozen=True)
class FrameSize:
    """Represents video frame dimensions."""

    width: int
    height: int

    @classmethod
    def from_string(cls, size_str: str) -> FrameSize:
        """Parse frame size from 'WIDTHxHEIGHT' string."""
        parts = size_str.lower().split("x")
        if len(parts) != 2:
            msg = f"Invalid frame size format: {size_str}"
            raise ValueError(msg)
        return cls(width=int(parts[0]), height=int(parts[1]))

    @property
    def as_tuple(self) -> tuple[int, int]:
        """Return as (width, height) tuple for OpenCV."""
        return (self.width, self.height)

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


@dataclass
class VideoConfig:
    """Configuration for video generation."""

    origin: str
    destination: str
    output_path: Path
    fps: int = 16
    frame_size: FrameSize = FrameSize(640, 480)
    max_workers: int = 8
    codec: str = "mp4v"

    # Drive-by mode settings
    driveby: bool = False
    center_coord: Coordinate | None = None
    object_height: float = 0.0

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.driveby and self.center_coord is None:
            msg = "center_coord required when driveby is True"
            raise ValueError(msg)
        if self.fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        if self.max_workers <= 0:
            msg = "max_workers must be positive"
            raise ValueError(msg)
        # Convert string paths to Path objects
        if isinstance(self.output_path, str):
            object.__setattr__(self, "output_path", Path(self.output_path))


@dataclass
class RouteData:
    """Represents a route with coordinates."""

    origin: str
    destination: str
    coordinates: list[Coordinate]

    @property
    def num_frames(self) -> int:
        """Number of frames in the route."""
        return len(self.coordinates)

    @property
    def distance_km(self) -> float:
        """Approximate total distance in kilometers."""
        from streetview_simulator.calculations import calculate_distance

        total = 0.0
        for i in range(len(self.coordinates) - 1):
            total += calculate_distance(
                self.coordinates[i],
                self.coordinates[i + 1],
            )
        return total
