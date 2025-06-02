#!/bin/bash

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    exit 1
fi

# Add project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Starting database population..."
python processors/resume_processor.py

if [ $? -eq 0 ]; then
    echo "Database population completed successfully"
    echo "Starting Streamlit application..."
    streamlit run app.py
else
    echo "Error: Database population failed"
    exit 1
fi
