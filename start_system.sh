#!/bin/bash
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Real-time Credit Card Fraud Prevention System             ║"
echo "║  DIPLOMA PROJECT - Network Security (IITU 2026)            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1️⃣  Installing dependencies..."
pip install -q -r requirements.txt
echo "   ✓ Dependencies installed"
echo ""

echo "2️⃣  Training ML models (ensemble + anomaly detection)..."
python3 -m train.train_model
echo ""

echo "3️⃣  Starting FastAPI server..."
echo "   🚀 API starting on http://localhost:8000"
echo "   📊 Dashboard: http://localhost:8000"
echo "   📝 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
