#!/bin/bash
# setup.sh - Setup script for AI Employee

echo "=========================================="
echo "AI Employee - Silver Tier Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.13"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.13+ required. Found: $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"
echo ""

# Create directories
echo "Creating directory structure..."
mkdir -p vault/{Inbox,Needs_Action,In_Progress,Plans,Pending_Approval,Approved,Rejected,Done,Briefings,Accounting,Logs,Templates,config}
mkdir -p config
mkdir -p logs
echo "✓ Directories created"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
echo "✓ Playwright browsers installed"
echo ""

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it with your credentials."
else
    echo "✓ .env file already exists"
fi
echo ""

# Setup Gmail authentication
echo "=========================================="
echo "Gmail Authentication Setup"
echo "=========================================="
echo ""
echo "To use Gmail features, you need to:"
echo "1. Go to https://console.cloud.google.com/"
echo "2. Create a new project"
echo "3. Enable Gmail API"
echo "4. Create OAuth credentials (Desktop app)"
echo "5. Download credentials.json and place it in config/"
echo ""
read -p "Do you have credentials.json ready? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f config/credentials.json ]; then
        echo "Running Gmail authentication..."
        python3 .claude/skills/gmail-watcher/scripts/gmail_auth.py
    else
        echo "ERROR: config/credentials.json not found!"
        echo "Please place your credentials.json in the config/ folder."
    fi
else
    echo "Skipping Gmail authentication. You can run it later with:"
    echo "  python3 .claude/skills/gmail-watcher/scripts/gmail_auth.py"
fi
echo ""

# Setup WhatsApp
echo "=========================================="
echo "WhatsApp Setup"
echo "=========================================="
echo ""
echo "WhatsApp Web requires scanning a QR code."
echo "Run the following command to set up:"
echo "  python3 .claude/skills/whatsapp-watcher/scripts/whatsapp_watcher.py --vault-path ./vault --show-browser --once"
echo ""

# Final instructions
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run verification: python scripts/verify_setup.py"
echo "3. Start the orchestrator: python orchestrator.py --vault-path ./vault"
echo ""
echo "Or use PM2 for production:"
echo "  pm2 start ecosystem.config.js"
echo ""
