# Google Street View Driving Simulator

Generate a time-lapse video of a Google Street View drive between two locations, with optional focus on a specific landmark. The simulator now supports both interactive prompts and a command-line interface, handles resource cleanup automatically, and produces MP4 output by default.

## Requirements

- Python 3.9 or newer
- A valid Google Maps Platform API key with access to the Directions API and Street View Static API
- Dependencies listed in `requirements.txt`

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Set your API key in the environment (recommended):

```bash
export GOOGLE_STREETVIEW_API_KEY="YOUR_KEY_HERE"
```

Alternatively, edit `StreetViewAPI.py` and set the `GOOGLE_STREETVIEW_API_KEY` constant.

## Usage

### Interactive mode

```bash
python GoogleStreetViewDrivingSimulator.py
```

Follow the prompts for origin, destination, file name, and output directory. Choose whether to focus on a landmark; the program will create the directory if needed.

### Command-line mode

```bash
python GoogleStreetViewDrivingSimulator.py \
  --origin "San Diego" \
  --destination "Los Angeles" \
  --output ./videos/sandiego_to_losangeles.mp4
```

Focus on a landmark during the drive:

```bash
python GoogleStreetViewDrivingSimulator.py \
  --origin "43.638891,-79.456817" \
  --destination "43.683613,-79.361742" \
  --driveby \
  --object-coordinate "43.642391,-79.387015" \
  --object-height 0.55 \
  --output ./videos/cntower.mp4
```

Key options:

- `--fps` – frames per second for the resulting video (`16` default)
- `--frame-size` – custom resolution such as `1280x720`
- `--max-workers` – limit concurrent image downloads
- `--api-key` – override the globally configured API key
- `--interactive` – force prompts even when arguments are supplied

## Output

- Videos are written as MP4 (`.mp4`) using the `mp4v` codec.
- Intermediate Street View frames are stored in a temporary directory and cleaned up automatically once the video is written.

## Notes

- Google APIs enforce usage quotas; heavy routes may take time to download because of throttling.
- The simulator validates inputs and will report API errors if the key is missing or does not have access to required services.
- To experiment with different camera angles, adjust `--max-workers`, `--frame-size`, or create smaller segments of the drive.
