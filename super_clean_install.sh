#!/bin/bash

# Super Clean Bluestar HA Integration Install
# This completely removes everything and installs fresh

echo "🧹 Super Clean Bluestar HA Integration Install..."

# Navigate to config directory
cd /config

# Stop Home Assistant completely
echo "⏹️ Stopping Home Assistant..."
ha core stop
sleep 3

# Remove ALL traces of old integration
echo "🗑️ Removing ALL old integration files..."
rm -rf custom_components/bluestar_ac
rm -rf .storage/custom_components
rm -rf .storage/bluestar_ac*
rm -rf .storage/core.config_entries
rm -rf .storage/core.device_registry
rm -rf .storage/core.entity_registry

# Clear Python cache
echo "🧹 Clearing Python cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Download fresh integration
echo "📥 Downloading fresh integration..."
wget -q -O bluestar-ha-v3.zip https://github.com/sankarhansdah/bluestar-ha-v3/archive/main.zip

# Extract and install
echo "📦 Installing integration..."
unzip -q -o bluestar-ha-v3.zip
cp -r bluestar-ha-v3-main/custom_components/bluestar_ac custom_components/
chmod -R 755 custom_components/bluestar_ac

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo "✅ Super clean install complete!"
echo "🚀 Integration should load in ~5-10 seconds"
echo "🔍 Check logs: ha core logs | grep bluestar"
echo "📱 Only phone/password fields will be shown in setup"


