#!/bin/bash

# FORCE CLEAR - Complete Home Assistant Cache Clearing Script
# This will force clear ALL caches and restart everything

echo "💥 FORCE CLEAR - Complete Home Assistant Cache Clearing"
echo "======================================================"

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

# Clear Home Assistant cache directories
echo "🧹 Clearing Home Assistant cache directories..."
rm -rf .homeassistant/__pycache__
rm -rf .homeassistant/custom_components/__pycache__
rm -rf .homeassistant/custom_components/bluestar_ac/__pycache__

# Clear any compiled Python files
echo "🧹 Clearing compiled Python files..."
find /usr/local/lib/python* -name "*bluestar*" -delete 2>/dev/null || true

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

# Verify installation with detailed checks
echo "🔍 Verifying installation..."
echo "📁 Checking files:"

if [ -f "custom_components/bluestar_ac/__init__.py" ]; then
    echo "✅ __init__.py found"
    grep -q "BLUESTAR_BASE_URL" custom_components/bluestar_ac/__init__.py && echo "✅ Base URL import found" || echo "❌ Base URL import missing"
else
    echo "❌ __init__.py missing"
fi

if [ -f "custom_components/bluestar_ac/climate.py" ]; then
    echo "✅ climate.py found"
    echo "📄 First 5 lines of climate.py:"
    head -5 custom_components/bluestar_ac/climate.py
else
    echo "❌ climate.py missing"
fi

if [ -f "custom_components/bluestar_ac/config_flow.py" ]; then
    echo "✅ config_flow.py found"
    grep -q "BLUESTAR_BASE_URL" custom_components/bluestar_ac/config_flow.py && echo "✅ Base URL in config flow found" || echo "❌ Base URL in config flow missing"
else
    echo "❌ config_flow.py missing"
fi

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Force restart Home Assistant
echo "▶️ Force restarting Home Assistant..."
ha core restart

echo ""
echo "✅ FORCE CLEAR installation complete!"
echo "🚀 Integration should load in ~10-15 seconds"
echo "📱 Only phone/password fields will be shown in setup"
echo "🔍 Check logs: ha core logs | grep bluestar"
echo ""
echo "Next steps:"
echo "1. Wait for Home Assistant to fully restart"
echo "2. Go to Configuration -> Integrations"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Bluestar Smart AC'"
echo "5. Enter your phone and password"
echo ""
echo "If you still get import errors, the issue is with Home Assistant's caching system."


