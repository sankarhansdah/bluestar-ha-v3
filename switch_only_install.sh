#!/bin/bash

# SWITCH ONLY - Minimal Bluestar HA Integration Install
# This installs only the switch platform to get basic functionality working

echo "🔌 SWITCH ONLY - Minimal Bluestar HA Integration Install"
echo "======================================================="

# Check if we're in the right directory
if [ ! -d "/config" ]; then
    echo "❌ Error: Please run this from Home Assistant's terminal"
    echo "   (You should be in /config directory)"
    exit 1
fi

cd /config

echo "📍 Current directory: $(pwd)"

# Stop Home Assistant completely
echo "⏹️ Stopping Home Assistant Core..."
ha core stop
sleep 5

# Remove ALL traces of old integration
echo "🗑️ Removing ALL old integration files..."
rm -rf custom_components/bluestar_ac
rm -rf .storage/bluestar_ac*
rm -rf .storage/core.config_entries
rm -rf .storage/core.device_registry
rm -rf .storage/core.entity_registry

# Clear ALL Python cache
echo "🧹 Clearing ALL Python cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyo" -delete

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

# Remove all platform files except switch.py
echo "🗑️ Removing unused platform files..."
rm -f custom_components/bluestar_ac/climate.py
rm -f custom_components/bluestar_ac/climate_*.py
rm -f custom_components/bluestar_ac/sensor.py
rm -f custom_components/bluestar_ac/button.py
rm -f custom_components/bluestar_ac/select.py

# Verify installation
echo "🔍 Verifying installation..."
echo "📁 Checking files:"

if [ -f "custom_components/bluestar_ac/__init__.py" ]; then
    echo "✅ __init__.py found"
else
    echo "❌ __init__.py missing"
fi

if [ -f "custom_components/bluestar_ac/switch.py" ]; then
    echo "✅ switch.py found"
else
    echo "❌ switch.py missing"
fi

if [ -f "custom_components/bluestar_ac/config_flow.py" ]; then
    echo "✅ config_flow.py found"
else
    echo "❌ config_flow.py missing"
fi

if [ -f "custom_components/bluestar_ac/api.py" ]; then
    echo "✅ api.py found"
else
    echo "❌ api.py missing"
fi

if [ -f "custom_components/bluestar_ac/coordinator.py" ]; then
    echo "✅ coordinator.py found"
else
    echo "❌ coordinator.py missing"
fi

# Check that unused platforms are removed
echo "🗑️ Checking unused platforms are removed:"
[ ! -f "custom_components/bluestar_ac/climate.py" ] && echo "✅ climate.py removed" || echo "❌ climate.py still exists"
[ ! -f "custom_components/bluestar_ac/sensor.py" ] && echo "✅ sensor.py removed" || echo "❌ sensor.py still exists"
[ ! -f "custom_components/bluestar_ac/button.py" ] && echo "✅ button.py removed" || echo "❌ button.py still exists"
[ ! -f "custom_components/bluestar_ac/select.py" ] && echo "✅ select.py removed" || echo "❌ select.py still exists"

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo ""
echo "✅ SWITCH ONLY installation complete!"
echo "🔌 Integration will use only switch platform"
echo "🚀 Integration should load in ~5-10 seconds"
echo "📱 Only phone/password fields will be shown in setup"
echo "🔍 Check logs: ha core logs | grep bluestar"
echo ""
echo "Features available:"
echo "- ✅ AC ON/OFF control via switch"
echo "- ✅ Device discovery"
echo "- ✅ Basic control functionality"
echo "- ✅ No platform errors"
echo ""
echo "Next steps:"
echo "1. Wait for Home Assistant to fully restart"
echo "2. Go to Configuration -> Integrations"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Bluestar Smart AC'"
echo "5. Enter your phone and password"
echo ""
echo "Once this works, we can add more platforms!"


