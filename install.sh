#!/bin/bash
# ABOUTME: Installation script for Unix/Linux/Mac
# ABOUTME: Sets up virtual environment and dependencies

echo "[INFO] Personal Assistant Agent - Setup"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "[INFO] Python version: $python_version"

# Create virtual environment
echo "[INFO] Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
echo "[INFO] Running setup tests..."
python test_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "[OK] Installation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Set your API key: export ANTHROPIC_API_KEY=your_key_here"
    echo "2. Activate venv: source venv/bin/activate"
    echo "3. Run assistant: python main.py"
    echo "4. See USAGE.md for detailed guide"
else
    echo "[ERROR] Installation failed. Check errors above."
    exit 1
fi
