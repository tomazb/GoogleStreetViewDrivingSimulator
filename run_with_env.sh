#!/bin/bash
# Load environment variables from .env file and run command

# Load .env file
set -a
source .env
set +a

# Activate virtual environment
source venv/bin/activate

# Run the command passed as arguments
"$@"
