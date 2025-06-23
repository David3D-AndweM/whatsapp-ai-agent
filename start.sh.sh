#!/bin/bash

# Resilient Equity WhatsApp AI Agent Startup Script

echo "🌱 Starting Resilient Equity WhatsApp AI Agent..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your API keys before running the agent."
    echo ""
    echo "Required configuration:"
    echo "- WHATSAPP_TOKEN: Your WhatsApp Business API token"
    echo "- WHATSAPP_PHONE_NUMBER_ID: Your phone number ID (already set)"
    echo "- VERIFY_TOKEN: Webhook verification token (already set)"
    echo "- OPENAI_API_KEY: Optional, for AI responses"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Start the application
echo "🚀 Starting WhatsApp AI Agent..."
echo ""
echo "Dashboard: http://localhost:5000"
echo "Webhook: http://localhost:5000/webhook"
echo "Health: http://localhost:5000/health"
echo ""
echo "Press Ctrl+C to stop the agent"
echo ""

python app.py