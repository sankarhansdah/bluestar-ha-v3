#!/bin/bash

# Force Reinstall Bluestar HA Integration
# This script completely removes and reinstalls the integration

echo "🔄 Force Reinstalling Bluestar HA Integration..."

# Navigate to config directory
cd /config

# Stop Home Assistant first
echo "⏹️ Stopping Home Assistant..."
ha core stop

# Wait a moment
sleep 3

# Remove old integration completely
echo "🗑️ Removing old integration..."
rm -rf custom_components/bluestar_ac

# Clear any cached files
echo "🧹 Clearing cache..."
rm -rf .storage/custom_components
rm -rf .storage/bluestar_ac*

# Download fresh integration
echo "📥 Downloading fresh integration..."
wget -O bluestar-ha-v3.zip https://github.com/sankarhansdah/bluestar-ha-v3/archive/main.zip

# Extract and install
echo "📦 Installing integration..."
unzip -o bluestar-ha-v3.zip
cp -r bluestar-ha-v3-main/custom_components/bluestar_ac custom_components/
chmod -R 755 custom_components/bluestar_ac

# Cleanup
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip

# Start Home Assistant
echo "▶️ Starting Home Assistant..."
ha core start

echo "✅ Force reinstall complete!"
echo "🔍 Check Home Assistant logs: ha core logs"


