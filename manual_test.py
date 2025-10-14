#!/usr/bin/env python
"""
Manual test script for Street View Simulator with real API key.

Usage:
    export GOOGLE_STREETVIEW_API_KEY="your_key_here"
    python manual_test.py
"""

import os
import sys
from pathlib import Path

from streetview_simulator.api import fetch_route_coordinates, generate_drive_video


def check_api_key():
    """Check if API key is available."""
    api_key = os.environ.get("GOOGLE_STREETVIEW_API_KEY", "").strip()
    if not api_key:
        print("❌ ERROR: GOOGLE_STREETVIEW_API_KEY environment variable is not set")
        print()
        print("Please set it with:")
        print('  export GOOGLE_STREETVIEW_API_KEY="your_key_here"')
        print()
        sys.exit(1)
    print(f"✓ API key found (length: {len(api_key)})")
    return api_key


def test_fetch_route():
    """Test fetching route coordinates."""
    print("\n" + "=" * 50)
    print("Test 1: Fetch Route Coordinates")
    print("=" * 50)

    try:
        print("Fetching route from Times Square to Empire State Building...")
        coords = fetch_route_coordinates(
            origin="Times Square, New York, NY",
            destination="Empire State Building, New York, NY",
        )
        print(f"✓ Successfully fetched {len(coords)} coordinates")
        print(f"  First coordinate: {coords[0]}")
        print(f"  Last coordinate: {coords[-1]}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_generate_video():
    """Test generating a video."""
    print("\n" + "=" * 50)
    print("Test 2: Generate Video")
    print("=" * 50)

    output_dir = Path("test_videos")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "manual_test.mp4"

    try:
        print("Generating video for short route...")
        print("This may take 1-3 minutes depending on route length...")

        result = generate_drive_video(
            origin="Times Square, New York, NY",
            destination="Empire State Building, New York, NY",
            output_path=str(output_path),
            driveby=False,
            fps=10,
            frame_size=(640, 480),
            max_workers=4,
        )

        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✓ Video created successfully!")
            print(f"  Location: {output_path}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
        else:
            print("✗ Video file not found")
            return False

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_driveby_mode():
    """Test driveby mode (optional, takes longer)."""
    print("\n" + "=" * 50)
    print("Test 3: Drive-by Mode (Optional)")
    print("=" * 50)

    response = input("Run drive-by test? This takes longer (y/n): ").lower()
    if response != "y":
        print("Skipped.")
        return True

    output_dir = Path("test_videos")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "driveby_test.mp4"

    try:
        print("Generating drive-by video...")
        print("This may take 5-10 minutes...")

        # Example: Drive past the Statue of Liberty
        result = generate_drive_video(
            origin="40.7128,-74.0060",  # NYC
            destination="40.6892,-74.0445",  # Near Statue of Liberty
            output_path=str(output_path),
            driveby=True,
            centercoord=(40.6892, -74.0445),  # Statue of Liberty
            height=0.093,  # ~93 meters
            fps=16,
            frame_size=(1280, 720),
            max_workers=4,
        )

        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"✓ Drive-by video created successfully!")
            print(f"  Location: {output_path}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
        else:
            print("✗ Video file not found")
            return False

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Street View Simulator - Manual API Test")
    print("=" * 50)

    # Check API key
    api_key = check_api_key()

    # Run tests
    results = []

    results.append(("Fetch Route", test_fetch_route()))
    results.append(("Generate Video", test_generate_video()))
    results.append(("Drive-by Mode", test_driveby_mode()))

    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! Your API key is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
