#!/bin/bash

# Nuclear Clean Bluestar HA Integration Install
# This completely wipes everything and forces a fresh install

echo "💥 NUCLEAR CLEAN Bluestar HA Integration Install..."

# Navigate to config directory
cd /config

# Stop Home Assistant completely
echo "⏹️ Stopping Home Assistant..."
ha core stop
sleep 5

# Remove ALL traces of old integration
echo "🗑️ Removing ALL old integration files..."
rm -rf custom_components/bluestar_ac
rm -rf .storage/custom_components
rm -rf .storage/bluestar_ac*
rm -rf .storage/core.config_entries
rm -rf .storage/core.device_registry
rm -rf .storage/core.entity_registry

# Clear ALL Python cache
echo "🧹 Clearing ALL Python cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyo" -delete

# Clear Home Assistant cache
echo "🧹 Clearing Home Assistant cache..."
rm -rf .homeassistant/__pycache__
rm -rf .homeassistant/custom_components/__pycache__

# Download fresh integration
echo "📥 Downloading fresh integration..."
wget -q -O bluestar-ha-v3.zip https://github.com/sankarhansdah/bluestar-ha-v3/archive/main.zip

# Extract and install
echo "📦 Installing integration..."
unzip -q -o bluestar-ha-v3.zip
cp -r bluestar-ha-v3-main/custom_components/bluestar_ac custom_components/
chmod -R 755 custom_components/bluestar_ac

# Verify the files are correct
echo "🔍 Verifying installation..."
if [ -f "custom_components/bluestar_ac/__init__.py" ]; then
    echo "✅ __init__.py found"
    grep -q "BLUESTAR_BASE_URL" custom_components/bluestar_ac/__init__.py && echo "✅ Base URL import found" || echo "❌ Base URL import missing"
else
    echo "❌ __init__.py missing"
fi

if [ -f "custom_components/bluestar_ac/config_flow.py" ]; then
    echo "✅ config_flow.py found"
    grep -q "BLUESTAR_BASE_URL" custom_components/bluestar_ac/config_flow.py && echo "✅ Base URL in config flow found" || echo "❌ Base URL in config flow missing"
else
    echo "❌ config_flow.py missing"
fi

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo "✅ Nuclear clean install complete!"
echo "🚀 Integration should load in ~5-10 seconds"
echo "🔍 Check logs: ha core logs | grep bluestar"
echo "📱 Only phone/password fields will be shown in setup"
echo "🌐 URLs are now properly set from constants"
