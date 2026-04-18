#!/bin/bash
# Court Automation Suite - Setup Script
set -e

echo "⚖️  Court Automation Suite - Setup"
echo "=================================="

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required"; exit 1; }

echo "  ✅ Python $(python3 --version | cut -d' ' -f2)"
echo "  ✅ Node.js $(node --version)"
echo "  ✅ npm $(npm --version)"

# Create virtual environment
echo ""
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✅ Virtual environment created"
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✅ Python dependencies installed"

# Install frontend dependencies
echo ""
echo "🎨 Setting up frontend..."
cd frontend
npm install --legacy-peer-deps
cd ..
echo "  ✅ Frontend dependencies installed"

# Setup environment
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✅ .env file created from .env.example"
    echo "  ⚠️  Please edit .env with your API keys and credentials"
else
    echo "  ✅ .env file already exists"
fi

# Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/pdfs data/logs credentials
echo "  ✅ Data directories created"

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your configuration"
echo "  2. Start MongoDB and Redis (or use Docker)"
echo "  3. Run: uvicorn backend.main:app --reload"
echo "  4. Run: cd frontend && npm run dev"
echo "  5. Optionally seed data: python scripts/seed_data.py"
