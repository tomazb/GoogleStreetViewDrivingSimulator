# Using the .env File for API Key

## Quick Start

Your `.env` file already contains your API key. To use it:

### Method 1: Use the Helper Script (Easiest)

```bash
./run_with_env.sh streetview-simulator [options]
```

**Example:**
```bash
./run_with_env.sh streetview-simulator \
  --origin "Times Square, NYC" \
  --destination "Central Park, NYC" \
  --output myvideo.mp4
```

### Method 2: Source .env Manually

```bash
# Load environment variables
set -a
source .env
set +a

# Activate virtual environment
source venv/bin/activate

# Run command
streetview-simulator [options]
```

### Method 3: Use with Test Scripts

The test scripts now automatically load `.env`:

```bash
./test_with_api.sh          # Automated test suite
python manual_test.py       # Interactive Python tests
```

## Your Current Setup

✅ **API Key**: Stored in `.env` file  
✅ **Helper Script**: `run_with_env.sh` created  
✅ **Test Scripts**: Updated to auto-load `.env`

## Examples

### Simple Route
```bash
./run_with_env.sh streetview-simulator \
  --origin "43.65,-79.38" \
  --destination "43.68,-79.36" \
  --output toronto_drive.mp4
```

### Drive-by Mode (CN Tower)
```bash
./run_with_env.sh streetview-simulator \
  --origin "43.638891,-79.456817" \
  --destination "43.683613,-79.361742" \
  --driveby \
  --object-coordinate "43.642391,-79.387015" \
  --object-height 0.55 \
  --output cntower.mp4
```

### High Quality Video
```bash
./run_with_env.sh streetview-simulator \
  --origin "Times Square, NYC" \
  --destination "Brooklyn Bridge, NYC" \
  --frame-width 1920 \
  --frame-height 1080 \
  --fps 30 \
  --output nyc_hd.mp4
```

## Troubleshooting

### Command Not Found

If you see "command not found", make sure to:
1. Use `./run_with_env.sh` (includes `./`)
2. Or activate venv manually: `source venv/bin/activate`

### API Key Not Working

If you see "API key missing" error:
1. Check `.env` file exists: `cat .env`
2. Make sure format is: `GOOGLE_STREETVIEW_API_KEY=your_key_here` (no quotes, no spaces)
3. Use `./run_with_env.sh` script

### Invalid API Key

If you see "REQUEST_DENIED":
1. Verify key in Google Cloud Console
2. Enable these APIs:
   - Street View Static API
   - Directions API
3. Check billing is enabled

## Security Note

⚠️ **Never commit `.env` to git!**  
The `.gitignore` file already excludes `.env` to protect your API key.
