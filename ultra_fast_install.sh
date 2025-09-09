#!/bin/bash

# Ultra-Fast Bluestar HA Integration Install
# This version prioritizes speed over MQTT features

echo "⚡ Ultra-Fast Bluestar HA Integration Install..."

# Navigate to config directory
cd /config

# Stop Home Assistant
echo "⏹️ Stopping Home Assistant..."
ha core stop
sleep 2

# Remove old integration completely
echo "🗑️ Removing old integration..."
rm -rf custom_components/bluestar_ac
rm -rf .storage/custom_components
rm -rf .storage/bluestar_ac*

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

echo "✅ Ultra-fast install complete!"
echo "🚀 Integration should load in ~5-10 seconds"
echo "🔍 Check logs: ha core logs | grep bluestar"


