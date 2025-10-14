import concurrent.futures
import contextlib
import logging
import os
import tempfile
import time
from typing import Iterable, List, Optional, Sequence, Tuple

try:
    import cv2
except ImportError as exc:
    raise ImportError("OpenCV (cv2) is required. Install it with 'pip install opencv-python'.") from exc

try:
    import requests
except ImportError as exc:
    raise ImportError("The 'requests' package is required. Install it with 'pip install requests'.") from exc
try:
    import polyline as polyline_lib

    def decode_polyline(s: str):
        return polyline_lib.decode(s)
except Exception:
    try:
        from polyline.codec import PolylineCodec

        _polyline_codec = PolylineCodec()

        def decode_polyline(s: str):
            return _polyline_codec.decode(s)
    except Exception as exc:
        raise ImportError("The 'polyline' package is required. Install it with 'pip install polyline'.") from exc

from Calculations import calculate_initial_compass_bearing, calculate_pitch

Coordinate = Tuple[float, float]
FrameSize = Tuple[int, int]

GOOGLE_STREETVIEW_API_KEY = ''  # Set this or use the GOOGLE_STREETVIEW_API_KEY environment variable.
GOOGLE_MAPS_DIRECTIONS_API = "https://maps.googleapis.com/maps/api/directions/json"
STREETVIEW_URL = "https://maps.googleapis.com/maps/api/streetview"
DEFAULT_VIDEO_CODEC = "mp4v"
DEFAULT_FPS = 16
DEFAULT_FRAME_SIZE: FrameSize = (640, 480)
DEFAULT_MAX_WORKERS = 8
REQUEST_TIMEOUT = 20
MAX_RETRIES = 4

logger = logging.getLogger(__name__)


def _resolve_api_key(explicit_key: Optional[str] = None) -> str:
    key = (explicit_key or os.environ.get("GOOGLE_STREETVIEW_API_KEY") or GOOGLE_STREETVIEW_API_KEY or "").strip()
    if not key:
        raise RuntimeError(
            "Google API key missing. Set the GOOGLE_STREETVIEW_API_KEY environment variable or pass api_key explicitly."
        )
    return key


def _coerce_bool(value: Optional[object]) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    if text in {"true", "t", "1", "yes", "y"}:
        return True
    if text in {"false", "f", "0", "no", "n"}:
        return False
    raise ValueError(f"Cannot interpret {value!r} as boolean.")


def _coerce_coordinate(value: object) -> Coordinate:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return float(value[0]), float(value[1])
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
        if len(parts) != 2:
            raise ValueError(f"Coordinate string must contain two comma-separated values: {value!r}")
        return float(parts[0]), float(parts[1])
    raise TypeError("Coordinate must be a sequence of two numbers or a comma-separated string.")


def _coerce_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return float(default)
    return float(value)


def _normalise_size(size: Optional[Sequence[int]]) -> FrameSize:
    if size is None:
        return DEFAULT_FRAME_SIZE
    if isinstance(size, str):
        parts = [p.strip() for p in size.lower().split("x")]
        if len(parts) != 2:
            raise ValueError("Frame size should be in the form WIDTHxHEIGHT, e.g. 640x480.")
        return int(parts[0]), int(parts[1])
    if len(size) != 2:
        raise ValueError("Frame size sequence must contain width and height.")
    return int(size[0]), int(size[1])


def build_coords(payload: dict) -> List[Coordinate]:
    routes = payload.get("routes")
    if not routes:
        raise ValueError("Google Directions API returned no routes.")
    result: List[Coordinate] = []
    for leg in routes[0].get("legs", []):
        for step in leg.get("steps", []):
            polyline_str = step.get("polyline", {}).get("points")
            if polyline_str:
                result.extend(decode_polyline(polyline_str))
    if not result:
        raise ValueError("Google Directions API returned an empty route.")
    return result


def unique(sequence: Iterable[Coordinate]) -> List[Coordinate]:
    seen = set()
    result: List[Coordinate] = []
    for lat, lng in sequence:
        key = (round(lat, 6), round(lng, 6))
        if key in seen:
            continue
        seen.add(key)
        result.append((float(lat), float(lng)))
    return result


def get_heading(start: Coordinate, end: Coordinate) -> str:
    return f"{calculate_initial_compass_bearing(start, end):.4f}"


def fetch_route_coordinates(
    origin: str,
    destination: str,
    *,
    session: Optional[requests.Session] = None,
    api_key: Optional[str] = None,
) -> List[Coordinate]:
    if not origin:
        raise ValueError("Origin must not be empty.")
    if not destination:
        raise ValueError("Destination must not be empty.")

    api_key = _resolve_api_key(api_key)
    params = {"origin": origin, "destination": destination, "key": api_key}

    manage_session = session is None
    session = session or requests.Session()

    try:
        response = session.get(GOOGLE_MAPS_DIRECTIONS_API, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to call Google Directions API: {exc}") from exc
    finally:
        if manage_session:
            session.close()

    status = payload.get("status")
    if status != "OK":
        message = payload.get("error_message") or status or "Unknown error"
        raise RuntimeError(f"Google Directions API error: {message}")

    coordinates = unique(build_coords(payload))
    if len(coordinates) < 2:
        raise RuntimeError("Directions API returned fewer than two coordinates.")
    return coordinates


def _download_single_image(
    session: requests.Session,
    params: dict,
    temp_dir: str,
    index: int,
) -> Tuple[int, str]:
    dest_path = os.path.join(temp_dir, f"{index:06d}.jpg")
    last_error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with session.get(STREETVIEW_URL, params=params, timeout=REQUEST_TIMEOUT, stream=True) as response:
                content_type = response.headers.get("Content-Type", "")
                if response.status_code == 200 and content_type.startswith("image"):
                    with open(dest_path, "wb") as handle:
                        for chunk in response.iter_content(chunk_size=65536):
                            handle.write(chunk)
                    return index, dest_path
                last_error = f"{response.status_code}: {response.text[:120]}"
        except requests.RequestException as exc:
            last_error = str(exc)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        sleep_for = min(2 ** attempt, 5)
        time.sleep(sleep_for)
    raise RuntimeError(f"Street View API request failed after {MAX_RETRIES} attempts for frame {index}: {last_error}")


@contextlib.contextmanager
def download_streetview_images(
    coordinates: Sequence[Coordinate],
    *,
    driveby: bool = False,
    centercoord: Optional[Coordinate] = None,
    height: float = 0.0,
    api_key: Optional[str] = None,
    frame_size: FrameSize = DEFAULT_FRAME_SIZE,
    max_workers: int = DEFAULT_MAX_WORKERS,
    session: Optional[requests.Session] = None,
    show_progress: bool = True,
):
    if not coordinates:
        raise ValueError("No coordinates provided.")
    api_key = _resolve_api_key(api_key)
    worker_count = max(1, min(max_workers, len(coordinates)))

    if driveby:
        if centercoord is None:
            raise ValueError("centercoord is required when driveby is True.")
        centercoord = _coerce_coordinate(centercoord)
        height = _coerce_float(height)
    else:
        centercoord = centercoord if centercoord is None else _coerce_coordinate(centercoord)
        height = _coerce_float(height)

    manage_session = session is None
    session = session or requests.Session()

    base_params = {
        "key": api_key,
        "size": f"{frame_size[0]}x{frame_size[1]}",
    }

    try:
        with tempfile.TemporaryDirectory(prefix="streetview_frames_") as temp_dir:
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
                total_frames = len(coordinates)
                futures = []
                for index, coord in enumerate(coordinates):
                    target = centercoord if driveby else coordinates[min(index + 3, total_frames - 1)]
                    heading = get_heading(coord, target)
                    pitch = calculate_pitch(centercoord, coord, height) if driveby else "0.0000"
                    params = {
                        **base_params,
                        "location": f"{coord[0]},{coord[1]}",
                        "heading": heading,
                        "pitch": pitch,
                    }
                    futures.append(executor.submit(_download_single_image, session, params, temp_dir, index))

                ordered_paths: List[str] = [""] * total_frames
                completed = 0
                try:
                    for future in concurrent.futures.as_completed(futures):
                        frame_index, path = future.result()
                        ordered_paths[frame_index] = path
                        completed += 1
                        if show_progress:
                            print(f"Downloaded {completed}/{total_frames} frames", end="\r", flush=True)
                finally:
                    if show_progress:
                        print()

                if any(not path for path in ordered_paths):
                    raise RuntimeError("Failed to download one or more frames.")

                yield ordered_paths
    finally:
        if manage_session:
            session.close()


def make_video(
    images: Sequence[str],
    output_path: str,
    *,
    fps: int = DEFAULT_FPS,
    frame_size: Optional[FrameSize] = None,
    is_color: bool = True,
    codec: str = DEFAULT_VIDEO_CODEC,
    create_dirs: bool = True,
) -> None:
    if not images:
        raise ValueError("No images provided to build the video.")

    first_frame = cv2.imread(images[0])
    if first_frame is None:
        raise RuntimeError(f"Unable to load frame {images[0]}")

    if frame_size is None:
        height, width = first_frame.shape[:2]
        frame_size = (width, height)

    if create_dirs:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*codec)
    writer = cv2.VideoWriter(output_path, fourcc, fps, frame_size, is_color)
    if not writer.isOpened():
        raise RuntimeError(f"Unable to open video writer for {output_path}")

    try:
        if (first_frame.shape[1], first_frame.shape[0]) != frame_size:
            first_frame = cv2.resize(first_frame, frame_size)
        writer.write(first_frame)
        for image in images[1:]:
            frame = cv2.imread(image)
            if frame is None:
                raise RuntimeError(f"Unable to load frame {image}")
            if (frame.shape[1], frame.shape[0]) != frame_size:
                frame = cv2.resize(frame, frame_size)
            writer.write(frame)
    finally:
        writer.release()


def save_location(create_missing: bool = True) -> str:
    while True:
        outputlocation = input("Where do you want to save this file?: \n").strip()
        if not outputlocation:
            print("Path must not be empty.")
            continue
        if os.path.isdir(outputlocation):
            return outputlocation
        if create_missing:
            try:
                os.makedirs(outputlocation, exist_ok=True)
                return outputlocation
            except OSError as exc:
                print(f"Unable to create directory {outputlocation}: {exc}")
        else:
            print(f"Invalid path: {outputlocation}")


def _ensure_extension(filename: str, default_ext: str) -> str:
    filename = filename.strip()
    root, ext = os.path.splitext(filename)
    if not root:
        raise ValueError("File name must not be empty.")
    if not ext:
        return f"{filename}{default_ext}"
    return filename


def generate_drive_video(
    *,
    origin: str,
    destination: str,
    output_path: str,
    driveby: bool = False,
    centercoord: Optional[Coordinate] = None,
    height: float = 0.0,
    fps: int = DEFAULT_FPS,
    frame_size: Optional[Sequence[int]] = None,
    max_workers: int = DEFAULT_MAX_WORKERS,
    api_key: Optional[str] = None,
    create_output_dir: bool = True,
) -> str:
    frame_size_tuple = _normalise_size(frame_size)
    api_key = _resolve_api_key(api_key)

    with requests.Session() as session:
        coordinates = fetch_route_coordinates(origin, destination, session=session, api_key=api_key)
        with download_streetview_images(
            coordinates,
            driveby=driveby,
            centercoord=centercoord,
            height=height,
            api_key=api_key,
            frame_size=frame_size_tuple,
            max_workers=max_workers,
            session=session,
        ) as frames:
            make_video(
                frames,
                output_path,
                fps=fps,
                frame_size=frame_size_tuple,
                codec=DEFAULT_VIDEO_CODEC,
                create_dirs=create_output_dir,
            )
    return output_path


def construct_video(
    *,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    driveby: Optional[object] = None,
    centercoord: Optional[object] = None,
    height: Optional[object] = None,
    output_path: Optional[str] = None,
    output_directory: Optional[str] = None,
    output_name: Optional[str] = None,
    fps: int = DEFAULT_FPS,
    frame_size: Optional[Sequence[int]] = None,
    max_workers: int = DEFAULT_MAX_WORKERS,
    api_key: Optional[str] = None,
    create_output_dir: bool = True,
) -> str:
    origin = (origin or input("Input Origin: ").strip())
    while not origin:
        print("Origin is required.")
        origin = input("Input Origin: ").strip()

    destination = (destination or input("Input Destination: ").strip())
    while not destination:
        print("Destination is required.")
        destination = input("Input Destination: ").strip()

    driveby_flag = _coerce_bool(driveby if driveby is not None else input("Look around an object? Type True or False: "))

    if driveby_flag:
        centercoord = _coerce_coordinate(centercoord or input("Give object coordinate:"))
        height_value = _coerce_float(height or input("Give object height in km:"))
        name_prompt = "Name of File: \n"
    else:
        centercoord = None
        height_value = _coerce_float(height, 0.0)
        print("Generating a drive time-lapse")
        name_prompt = "Please type in name of file: \n"

    if output_path:
        output_path = _ensure_extension(output_path, ".mp4")
        output_directory = os.path.dirname(os.path.abspath(output_path))
        output_name = os.path.basename(output_path)
    else:
        desired_name = output_name or input(name_prompt).strip()
        while not desired_name:
            print("File name is required.")
            desired_name = input(name_prompt).strip()
        output_name = _ensure_extension(desired_name, ".mp4")
        output_directory = output_directory or save_location(create_missing=create_output_dir)
        output_path = os.path.join(output_directory, output_name)

    frame_size_tuple = _normalise_size(frame_size)

    generate_drive_video(
        origin=origin,
        destination=destination,
        output_path=output_path,
        driveby=driveby_flag,
        centercoord=centercoord,
        height=height_value,
        fps=fps,
        frame_size=frame_size_tuple,
        max_workers=max_workers,
        api_key=api_key,
        create_output_dir=create_output_dir,
    )
    print(f"Video Generated Successfully at {output_path}")
    return output_path
