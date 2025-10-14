#!/bin/bash
# Test different FPS values on a short route

echo "Testing different FPS values..."
echo "This will create 4 short videos with different speeds."
echo ""

# Short test route
ORIGIN="43.65,-79.38"
DEST="43.66,-79.37"

# Test 1: Ultra slow (1 FPS)
echo "1. Creating video at 1 FPS (ultra slow)..."
./run_with_env.sh streetview-simulator \
  --origin "$ORIGIN" \
  --destination "$DEST" \
  --fps 1 \
  --output test_videos/test_1fps.mp4

# Test 2: Very slow (3 FPS)
echo "2. Creating video at 3 FPS (very slow)..."
./run_with_env.sh streetview-simulator \
  --origin "$ORIGIN" \
  --destination "$DEST" \
  --fps 3 \
  --output test_videos/test_3fps.mp4

# Test 3: Slow (5 FPS)
echo "3. Creating video at 5 FPS (slow)..."
./run_with_env.sh streetview-simulator \
  --origin "$ORIGIN" \
  --destination "$DEST" \
  --fps 5 \
  --output test_videos/test_5fps.mp4

# Test 4: Normal (16 FPS - default)
echo "4. Creating video at 16 FPS (normal)..."
./run_with_env.sh streetview-simulator \
  --origin "$ORIGIN" \
  --destination "$DEST" \
  --fps 16 \
  --output test_videos/test_16fps.mp4

echo ""
echo "Done! Compare the videos:"
ls -lh test_videos/test_*fps.mp4
