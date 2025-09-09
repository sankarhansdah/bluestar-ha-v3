#!/bin/bash

# Bluestar Smart AC Home Assistant Integration - Installation Script
# Version 3.0.0

set -e

echo "🚀 Installing Bluestar Smart AC Integration v3.0.0..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in Home Assistant
if [ ! -d "/config" ]; then
    print_error "This script must be run in Home Assistant Terminal"
    exit 1
fi

# Create custom_components directory if it doesn't exist
if [ ! -d "/config/custom_components" ]; then
    print_status "Creating custom_components directory..."
    mkdir -p /config/custom_components
fi

# Create bluestar_ac directory
BLUESTAR_DIR="/config/custom_components/bluestar_ac"
if [ -d "$BLUESTAR_DIR" ]; then
    print_warning "Removing existing integration..."
    rm -rf "$BLUESTAR_DIR"
fi

print_status "Creating bluestar_ac directory..."
mkdir -p "$BLUESTAR_DIR"

# Download integration files
print_status "Downloading integration files..."

# Core files
wget -q -O "$BLUESTAR_DIR/__init__.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/__init__.py"
wget -q -O "$BLUESTAR_DIR/api.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/api.py"
wget -q -O "$BLUESTAR_DIR/coordinator.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/coordinator.py"
wget -q -O "$BLUESTAR_DIR/config_flow.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/config_flow.py"
wget -q -O "$BLUESTAR_DIR/const.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/const.py"
wget -q -O "$BLUESTAR_DIR/manifest.json" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/manifest.json"
wget -q -O "$BLUESTAR_DIR/strings.json" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/strings.json"

# Platform files
wget -q -O "$BLUESTAR_DIR/climate.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/climate.py"
wget -q -O "$BLUESTAR_DIR/switch.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/switch.py"
wget -q -O "$BLUESTAR_DIR/sensor.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/sensor.py"
wget -q -O "$BLUESTAR_DIR/select.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/select.py"
wget -q -O "$BLUESTAR_DIR/button.py" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/button.py"

# Translations
mkdir -p "$BLUESTAR_DIR/translations"
wget -q -O "$BLUESTAR_DIR/translations/en.json" "https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/custom_components/bluestar_ac/translations/en.json"

# Verify installation
print_status "Verifying installation..."

# Check if all files exist
REQUIRED_FILES=(
    "__init__.py"
    "api.py"
    "coordinator.py"
    "config_flow.py"
    "const.py"
    "manifest.json"
    "strings.json"
    "climate.py"
    "switch.py"
    "sensor.py"
    "select.py"
    "button.py"
    "translations/en.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$BLUESTAR_DIR/$file" ]; then
        print_error "Missing file: $file"
        exit 1
    fi
done

print_success "All files downloaded successfully!"

# Set proper permissions
print_status "Setting file permissions..."
chmod -R 755 "$BLUESTAR_DIR"

# Basic syntax check (without Home Assistant imports)
print_status "Checking Python syntax..."

# Check const.py (no HA imports)
python3 -c "
import sys
sys.path.insert(0, '$BLUESTAR_DIR')
try:
    import ast
    with open('$BLUESTAR_DIR/const.py', 'r') as f:
        ast.parse(f.read())
    print('const.py syntax OK')
except SyntaxError as e:
    print(f'const.py syntax error: {e}')
    sys.exit(1)
" || {
    print_error "Syntax error in const.py"
    exit 1
}

# Check other files for basic syntax (without imports)
for file in "__init__.py" "api.py" "coordinator.py" "config_flow.py" "climate.py" "switch.py" "sensor.py" "select.py" "button.py"; do
    python3 -c "
import sys
import ast
try:
    with open('$BLUESTAR_DIR/$file', 'r') as f:
        content = f.read()
    # Remove import lines for syntax check
    lines = content.split('\n')
    filtered_lines = []
    for line in lines:
        if not line.strip().startswith('from homeassistant') and not line.strip().startswith('import homeassistant'):
            filtered_lines.append(line)
    filtered_content = '\n'.join(filtered_lines)
    ast.parse(filtered_content)
    print('$file syntax OK')
except SyntaxError as e:
    print(f'$file syntax error: {e}')
    sys.exit(1)
" || {
    print_error "Syntax error in $file"
    exit 1
}
done

print_success "Python syntax check passed!"

# Installation complete
print_success "🎉 Bluestar Smart AC Integration v3.0.0 installed successfully!"
echo ""
print_status "📋 Next Steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Settings → Devices & Services"
echo "3. Click 'Add Integration'"
echo "4. Search for 'Bluestar Smart AC'"
echo "5. Enter your phone number and password"
echo ""
print_status "📖 Documentation:"
echo "- README: https://github.com/sankarhansdah/bluestar-ha-v3"
echo "- Test Plan: See MANUAL_TEST_PLAN.md"
echo "- Troubleshooting: Check README troubleshooting section"
echo ""
print_status "🔧 Enable Debug Logging (optional):"
echo "Add to configuration.yaml:"
echo "logger:"
echo "  default: warning"
echo "  logs:"
echo "    custom_components.bluestar_ac: debug"
echo ""
print_success "Installation complete! 🏠❄️"
