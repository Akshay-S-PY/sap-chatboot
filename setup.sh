#!/bin/bash
# setup.sh - Automated setup script for SAP Chatbot

set -e

echo "🧩 SAP Intelligent Assistant - Setup"
echo "======================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env from template
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data/raw

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file if needed: nano .env"
echo "2. Build dataset: python tools/build_dataset.py"
echo "3. Build RAG index: python tools/embeddings.py"
echo "4. Run app: streamlit run app.py"
echo ""
