#!/bin/bash

# Bluestar Smart AC Home Assistant Integration Installation Script
# Version 3.0.0

set -e

echo "🏠 Bluestar Smart AC Home Assistant Integration v3.0"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "custom_components/bluestar_ac" ]; then
    echo "❌ Error: Please run this script from the bluestar-ha-v3 directory"
    exit 1
fi

# Check if Home Assistant is installed
HA_CONFIG_DIR=""
if [ -d "/config" ]; then
    HA_CONFIG_DIR="/config"
elif [ -d "$HOME/.homeassistant" ]; then
    HA_CONFIG_DIR="$HOME/.homeassistant"
elif [ -d "/usr/share/hassio/homeassistant" ]; then
    HA_CONFIG_DIR="/usr/share/hassio/homeassistant"
else
    echo "❌ Error: Home Assistant configuration directory not found"
    echo "Please specify the path to your Home Assistant configuration directory:"
    read -p "HA Config Directory: " HA_CONFIG_DIR
fi

if [ ! -d "$HA_CONFIG_DIR" ]; then
    echo "❌ Error: Directory $HA_CONFIG_DIR does not exist"
    exit 1
fi

echo "📁 Home Assistant Config Directory: $HA_CONFIG_DIR"

# Create custom_components directory if it doesn't exist
CUSTOM_COMPONENTS_DIR="$HA_CONFIG_DIR/custom_components"
if [ ! -d "$CUSTOM_COMPONENTS_DIR" ]; then
    echo "📂 Creating custom_components directory"
    mkdir -p "$CUSTOM_COMPONENTS_DIR"
fi

# Copy the integration files
echo "📋 Copying integration files..."
cp -r custom_components/bluestar_ac "$CUSTOM_COMPONENTS_DIR/"

# Set proper permissions
echo "🔐 Setting proper permissions..."
chmod -R 755 "$CUSTOM_COMPONENTS_DIR/bluestar_ac"

echo "✅ Installation completed successfully!"
echo ""
echo "🚀 Next Steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Bluestar Smart AC'"
echo "5. Enter your credentials and complete the setup"
echo ""
echo "📖 For detailed instructions, see the README.md file"
echo "🐛 For troubleshooting, check the Home Assistant logs"
echo ""
echo "🎉 Enjoy controlling your Bluestar AC units with Home Assistant!"
