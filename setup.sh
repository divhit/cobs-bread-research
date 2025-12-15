#!/bin/bash
# Setup script for COBS Bread Research Tool

echo "======================================"
echo "COBS Bread Research Tool - Setup"
echo "======================================"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To use the tool:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your Google API key:"
echo "   export GOOGLE_API_KEY='your-api-key-here'"
echo ""
echo "3. Run the research tool:"
echo "   python cobs_research.py \"COBS Bread, Your Location Here\""
echo ""
echo "Get your API key from: https://aistudio.google.com/apikey"
echo ""
