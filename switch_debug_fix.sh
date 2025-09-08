#!/bin/bash

# SWITCH DEBUG FIX - Fix SW1 Logging and Add Empty Data Check
# This fixes the SW1 logging issue and adds empty data detection

echo "🔧 SWITCH DEBUG FIX - Fix SW1 Logging and Add Empty Data Check"
echo "============================================================="

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

# Extract and update switch.py
echo "📦 Updating switch.py..."
unzip -q -o bluestar-ha-v3.zip
cp bluestar-ha-v3-main/custom_components/bluestar_ac/switch.py custom_components/bluestar_ac/switch.py
chmod 755 custom_components/bluestar_ac/switch.py

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo ""
echo "✅ Switch debug fix complete!"
echo "🔧 Fixed SW1 logging and added empty data detection"
echo "🚀 Check logs: ha core logs | grep -E '(SW1|SW2|SW_DATA_OK|SW_EMPTY|SW3|SW4|SW5)'"
echo ""
echo "Look for these log messages:"
echo "- SW1: Coordinator data keys (should show actual keys now)"
echo "- SW2: Full coordinator data"
echo "- SW_DATA_OK: Number of devices found"
echo "- SW_EMPTY: If coordinator data is empty"
echo "- SW3-SW5: Switch entity creation process"
