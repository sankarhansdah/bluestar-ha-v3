#!/bin/bash

# PLATFORM DEBUG UPDATE - Check Platform Loading
# This updates the integration to debug platform loading issues

echo "🔍 PLATFORM DEBUG UPDATE - Check Platform Loading"
echo "================================================"

# Check if we're in the right directory
if [ ! -d "/config" ]; then
    echo "❌ Error: Please run this from Home Assistant's terminal"
    echo "   (You should be in /config directory)"
    exit 1
fi

cd /config

echo "📍 Current directory: $(pwd)"

# Stop Home Assistant
echo "⏹️ Stopping Home Assistant..."
ha core stop
sleep 3

# Download fresh integration
echo "📥 Downloading fresh integration..."
wget -q -O bluestar-ha-v3.zip https://github.com/sankarhansdah/bluestar-ha-v3/archive/main.zip

# Extract and update files
echo "📦 Updating integration files..."
unzip -q -o bluestar-ha-v3.zip
cp bluestar-ha-v3-main/custom_components/bluestar_ac/__init__.py custom_components/bluestar_ac/__init__.py
cp bluestar-ha-v3-main/custom_components/bluestar_ac/switch.py custom_components/bluestar_ac/switch.py
chmod 755 custom_components/bluestar_ac/__init__.py
chmod 755 custom_components/bluestar_ac/switch.py

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo ""
echo "✅ Platform debug update complete!"
echo "🔍 Enhanced platform loading debugging installed"
echo "🚀 Check logs: ha core logs | grep -E '(B9|B10|SW_SETUP|SW1|SW2|SW3|SW4|SW5)'"
echo ""
echo "Look for these log messages:"
echo "- B9: Platform forwarding start"
echo "- B10: Platform forwarding complete"
echo "- SW_SETUP: Switch platform setup called"
echo "- SW1-SW5: Switch platform debug messages"


