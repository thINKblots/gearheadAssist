#!/bin/bash
# Setup script for Ollama server on Ubuntu/Debian VMs
# Run this on your cloud VM to set up Ollama with the gearhead8b model

set -e

echo "=== Ollama Server Setup for Gearhead Assist ==="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "Please don't run as root. Use a regular user with sudo privileges."
   exit 1
fi

# Install Ollama
echo "📦 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed"
else
    echo "✅ Ollama already installed"
fi

# Configure Ollama to accept external connections
echo ""
echo "🔧 Configuring Ollama for external access..."
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama
echo "✅ Ollama configured for external access"

# Wait for Ollama to start
echo ""
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Modelfile exists
if [ ! -f "Modelfile" ]; then
    echo "❌ Error: Modelfile not found in current directory"
    echo "Please upload your Modelfile to this directory first:"
    echo "  scp Modelfile user@$(hostname -I | awk '{print $1}'):~/"
    exit 1
fi

# Create the gearhead8b model
echo ""
echo "🤖 Creating gearhead8b model..."
ollama create gearhead8b -f Modelfile
echo "✅ Model created successfully"

# Test the model
echo ""
echo "🧪 Testing model..."
ollama run gearhead8b "test" --verbose
echo "✅ Model test complete"

# Display server info
echo ""
echo "================================================"
echo "✨ Setup Complete!"
echo "================================================"
echo ""
echo "Your Ollama server is running at:"
echo "  Internal: http://localhost:11434"
echo "  External: http://$(hostname -I | awk '{print $1}'):11434"
echo ""
echo "Model available: gearhead8b"
echo ""
echo "Next steps:"
echo "1. Set up HTTPS with Nginx (recommended for production)"
echo "   See DEPLOYMENT.md for instructions"
echo ""
echo "2. Configure firewall:"
echo "   sudo ufw allow 11434/tcp"
echo "   sudo ufw enable"
echo ""
echo "3. Add to Streamlit Cloud secrets:"
echo "   OLLAMA_HOST = \"http://$(hostname -I | awk '{print $1}'):11434\""
echo ""
echo "4. Monitor logs:"
echo "   journalctl -u ollama -f"
echo ""
