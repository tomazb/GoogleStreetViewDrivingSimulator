import argparse
import os
import sys

# Try to import from the new package first, fall back to the old module for backward compatibility
try:
    from streetview_simulator import api as StreetViewAPI
except ImportError:
    # If the package is not installed, try to use the local module
    try:
        import StreetViewAPI
    except ImportError as e:
        print("Error: Could not import streetview_simulator package or StreetViewAPI module.")
        print("Please install the package or ensure the modules are in the correct path.")
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Google Street View driving time-lapse.",
    )
    parser.add_argument("--origin", help="Starting point for the drive.")
    parser.add_argument("--destination", help="Destination for the drive.")
    driveby_group = parser.add_mutually_exclusive_group()
    driveby_group.add_argument(
        "--driveby",
        dest="driveby",
        action="store_true",
        help="Enable object focus mode.",
    )
    driveby_group.add_argument(
        "--no-driveby",
        dest="driveby",
        action="store_false",
        help="Disable object focus mode.",
    )
    parser.set_defaults(driveby=None)
    parser.add_argument(
        "--object-coordinate",
        help="Latitude,Longitude of the object to focus on when driveby is enabled.",
    )
    parser.add_argument(
        "--object-height",
        type=float,
        help="Object height in km used for pitch calculation when driveby is enabled.",
    )
    parser.add_argument("--output", help="Full path to the output video file.")
    parser.add_argument("--output-directory", help="Directory where the video will be stored.")
    parser.add_argument("--output-name", help="File name for the output video.")
    parser.add_argument(
        "--fps",
        type=int,
        default=StreetViewAPI.DEFAULT_FPS,
        help=f"Frames per second for the output video (default: {StreetViewAPI.DEFAULT_FPS}).",
    )
    parser.add_argument(
        "--frame-size",
        help="Frame size as WIDTHxHEIGHT (default: 640x480).",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=StreetViewAPI.DEFAULT_MAX_WORKERS,
        help=f"Maximum number of concurrent downloads (default: {StreetViewAPI.DEFAULT_MAX_WORKERS}).",
    )
    parser.add_argument("--api-key", help="Override the Google API key for this run.")
    parser.add_argument(
        "--no-create-output-dir",
        action="store_true",
        help="Do not create the output directory if it does not exist.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Force interactive mode even if command line arguments are provided.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    interactive = args.interactive or not (args.origin and args.destination)

    output_path = args.output
    if output_path:
        output_path = os.path.abspath(output_path)
    elif args.output_directory and args.output_name:
        output_path = os.path.join(args.output_directory, args.output_name)

    if interactive:
        StreetViewAPI.construct_video(
            origin=args.origin,
            destination=args.destination,
            driveby=args.driveby,
            centercoord=args.object_coordinate,
            height=args.object_height,
            output_path=output_path,
            output_directory=args.output_directory,
            output_name=args.output_name,
            fps=args.fps,
            frame_size=args.frame_size,
            max_workers=args.max_workers,
            api_key=args.api_key,
            create_output_dir=not args.no_create_output_dir,
        )
        return

    StreetViewAPI.generate_drive_video(
        origin=args.origin,
        destination=args.destination,
        output_path=output_path or os.path.join(args.output_directory or ".", args.output_name or "drive.mp4"),
        driveby=bool(args.driveby),
        centercoord=args.object_coordinate,
        height=args.object_height or 0.0,
        fps=args.fps,
        frame_size=args.frame_size,
        max_workers=args.max_workers,
        api_key=args.api_key,
        create_output_dir=not args.no_create_output_dir,
    )


if __name__ == '__main__':
    main()
