#!/bin/bash
# Test script for Google Street View Driving Simulator
# 
# Usage: ./test_with_api.sh
#
# The script will automatically load GOOGLE_STREETVIEW_API_KEY from .env file

set -e  # Exit on error

# Load .env file if it exists
if [ -f .env ]; then
    echo "Loading API key from .env file..."
    set -a
    source .env
    set +a
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Street View Simulator - API Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if API key is set
if [ -z "$GOOGLE_STREETVIEW_API_KEY" ]; then
    echo -e "${RED}ERROR: GOOGLE_STREETVIEW_API_KEY environment variable is not set${NC}"
    echo ""
    echo "Please set it with:"
    echo "  export GOOGLE_STREETVIEW_API_KEY=\"your_key_here\""
    echo ""
    echo "Or source your .env file if you have one"
    exit 1
fi

echo -e "${GREEN}✓ API key found${NC}"
echo ""

# Create output directory
OUTPUT_DIR="test_videos"
mkdir -p "$OUTPUT_DIR"
echo -e "${GREEN}✓ Created output directory: $OUTPUT_DIR${NC}"
echo ""

# Test 1: Very short route for quick testing
echo -e "${YELLOW}Test 1: Short route (Times Square to Empire State)${NC}"
echo "This should take 1-2 minutes..."
python -m streetview_simulator \
    --origin "Times Square, New York, NY" \
    --destination "Empire State Building, New York, NY" \
    --output "$OUTPUT_DIR/test1_short.mp4" \
    --fps 10

if [ -f "$OUTPUT_DIR/test1_short.mp4" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_DIR/test1_short.mp4" | cut -f1)
    echo -e "${GREEN}✓ Test 1 PASSED: Video created ($FILE_SIZE)${NC}"
else
    echo -e "${RED}✗ Test 1 FAILED: Video not created${NC}"
    exit 1
fi
echo ""

# Test 2: Slightly longer route
echo -e "${YELLOW}Test 2: Medium route (San Diego to La Jolla)${NC}"
echo "This may take 3-5 minutes..."
python -m streetview_simulator \
    --origin "San Diego, CA" \
    --destination "La Jolla, CA" \
    --output "$OUTPUT_DIR/test2_medium.mp4" \
    --fps 16

if [ -f "$OUTPUT_DIR/test2_medium.mp4" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_DIR/test2_medium.mp4" | cut -f1)
    echo -e "${GREEN}✓ Test 2 PASSED: Video created ($FILE_SIZE)${NC}"
else
    echo -e "${RED}✗ Test 2 FAILED: Video not created${NC}"
    exit 1
fi
echo ""

# Test 3: Test with coordinates (optional - comment out if you want faster testing)
# echo -e "${YELLOW}Test 3: Using coordinates (custom route)${NC}"
# python -m streetview_simulator \
#     --origin "40.7128,-74.0060" \
#     --destination "40.7589,-73.9851" \
#     --output "$OUTPUT_DIR/test3_coords.mp4" \
#     --fps 12
#
# if [ -f "$OUTPUT_DIR/test3_coords.mp4" ]; then
#     FILE_SIZE=$(du -h "$OUTPUT_DIR/test3_coords.mp4" | cut -f1)
#     echo -e "${GREEN}✓ Test 3 PASSED: Video created ($FILE_SIZE)${NC}"
# else
#     echo -e "${RED}✗ Test 3 FAILED: Video not created${NC}"
#     exit 1
# fi
# echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Output videos are in: $OUTPUT_DIR/"
ls -lh "$OUTPUT_DIR/"
echo ""
echo "You can view them with:"
echo "  vlc $OUTPUT_DIR/test1_short.mp4"
echo "  # or"
echo "  mpv $OUTPUT_DIR/test1_short.mp4"
