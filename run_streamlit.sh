#!/bin/bash
# Launcher script for Shadai Streamlit App

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed."
    echo "Installing streamlit..."
    pip install streamlit
fi

# Run the Streamlit app
echo "🚀 Starting Shadai Streamlit App..."
echo "📍 Opening browser at http://localhost:8501"
echo ""
streamlit run streamlit_app.py
