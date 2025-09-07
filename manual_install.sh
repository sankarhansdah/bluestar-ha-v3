#!/bin/bash

# Manual Bluestar HA Integration Install via Home Assistant Terminal
# Run this directly in Home Assistant's terminal

echo "🏠 Manual Bluestar HA Integration Install"
echo "========================================"

# Check if we're in the right directory
if [ ! -d "/config" ]; then
    echo "❌ Error: Please run this from Home Assistant's terminal"
    echo "   (You should be in /config directory)"
    exit 1
fi

cd /config

echo "📍 Current directory: $(pwd)"
echo "📋 Listing current custom_components:"
ls -la custom_components/ 2>/dev/null || echo "No custom_components directory found"

# Stop Home Assistant
echo "⏹️ Stopping Home Assistant..."
ha core stop
sleep 3

# Remove old integration completely
echo "🗑️ Removing old Bluestar integration..."
rm -rf custom_components/bluestar_ac
rm -rf .storage/bluestar_ac*

# Download fresh integration
echo "📥 Downloading fresh integration..."
wget -q -O bluestar-ha-v3.zip https://github.com/sankarhansdah/bluestar-ha-v3/archive/main.zip

if [ ! -f "bluestar-ha-v3.zip" ]; then
    echo "❌ Failed to download integration"
    exit 1
fi

# Extract and install
echo "📦 Installing integration..."
unzip -q -o bluestar-ha-v3.zip
cp -r bluestar-ha-v3-main/custom_components/bluestar_ac custom_components/
chmod -R 755 custom_components/bluestar_ac

# Verify installation
echo "🔍 Verifying installation..."
if [ -f "custom_components/bluestar_ac/__init__.py" ]; then
    echo "✅ __init__.py found"
else
    echo "❌ __init__.py missing"
fi

if [ -f "custom_components/bluestar_ac/climate.py" ]; then
    echo "✅ climate.py found"
else
    echo "❌ climate.py missing"
fi

if [ -f "custom_components/bluestar_ac/config_flow.py" ]; then
    echo "✅ config_flow.py found"
else
    echo "❌ config_flow.py missing"
fi

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo ""
echo "✅ Manual installation complete!"
echo "🚀 Integration should load in ~5-10 seconds"
echo "📱 Only phone/password fields will be shown in setup"
echo "🔍 Check logs: ha core logs | grep bluestar"
echo ""
echo "Next steps:"
echo "1. Go to Configuration -> Integrations"
echo "2. Click 'Add Integration'"
echo "3. Search for 'Bluestar Smart AC'"
echo "4. Enter your phone and password"
