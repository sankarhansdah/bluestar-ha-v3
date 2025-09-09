# 🏠 Bluestar Smart AC Home Assistant Integration - Installation Guide

## 📋 Prerequisites

- Home Assistant running (version 2023.1.0 or later)
- Bluestar Smart AC units connected to WiFi
- Bluestar account credentials (phone number and password)

## 🚀 Installation Methods

### Method 1: HACS Installation (Recommended)

#### Step 1: Install HACS (if not already installed)
```bash
# SSH into your Home Assistant
ssh root@your-ha-ip

# Install HACS
wget -q -O - https://install.hacs.xyz | bash -
```

#### Step 2: Add Custom Repository
1. Go to Home Assistant UI
2. Navigate to **HACS** → **Integrations**
3. Click **Custom Repositories** (3 dots menu)
4. Add repository: `https://github.com/sankarhansdah/bluestar-ha-v3`
5. Category: **Integration**
6. Click **Add**

#### Step 3: Install Integration
1. Search for **"Bluestar Smart AC"** in HACS
2. Click **Install**
3. Restart Home Assistant: `ha core restart`

### Method 2: Manual Installation

#### Step 1: SSH into Home Assistant
```bash
ssh root@your-ha-ip
```

#### Step 2: Navigate to config directory
```bash
cd /config
```

#### Step 3: Create custom_components directory
```bash
mkdir -p custom_components
```

#### Step 4: Download and install integration
```bash
# Download the integration
wget -O bluestar-ha-v3.zip https://github.com/sankarhansdah/bluestar-ha-v3/archive/main.zip

# Extract the files
unzip bluestar-ha-v3.zip

# Copy integration files
cp -r bluestar-ha-v3-main/custom_components/bluestar_ac custom_components/

# Set proper permissions
chmod -R 755 custom_components/bluestar_ac

# Clean up
rm -rf bluestar-ha-v3-main bluestar-ha-v3.zip
```

#### Step 5: Restart Home Assistant
```bash
ha core restart
```

### Method 3: Using Installation Script

#### Step 1: Download installation script
```bash
# SSH into Home Assistant
ssh root@your-ha-ip

# Download script
wget https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/install.sh

# Make executable
chmod +x install.sh

# Run installation
./install.sh
```

## ⚙️ Configuration

### Step 1: Add Integration
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Bluestar Smart AC"**
4. Click on the integration

### Step 2: Enter Credentials
- **Phone Number**: Your Bluestar account phone number (e.g., 9439614598)
- **Password**: Your Bluestar account password
- **API Base URL**: `https://api.bluestarindia.com/prod` (default)
- **MQTT Endpoint**: `a1b2c3d4e5f6g7-ats.iot.ap-south-1.amazonaws.com` (default)

### Step 3: Complete Setup
1. Click **Submit**
2. The integration will discover your AC units
3. Click **Finish**

## 🎛️ Usage

### Basic Control
```yaml
# Turn on AC and set to cool mode
service: climate.set_hvac_mode
target:
  entity_id: climate.bluestar_ac_living_room
data:
  hvac_mode: cool

# Set temperature
service: climate.set_temperature
target:
  entity_id: climate.bluestar_ac_living_room
data:
  temperature: 24
```

### Automation Example
```yaml
automation:
  - alias: "Turn on AC when hot"
    trigger:
      - platform: numeric_state
        entity_id: sensor.living_room_temperature
        above: 28
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.bluestar_ac_living_room
        data:
          hvac_mode: cool
      - service: climate.set_temperature
        target:
          entity_id: climate.bluestar_ac_living_room
        data:
          temperature: 24
```

## 🔧 Troubleshooting

### Check Integration Status
```bash
# Check Home Assistant logs
ha core logs

# Check specific integration logs
ha core logs | grep bluestar
```

### Common Issues

**Integration won't load:**
- Verify credentials are correct
- Ensure AC units are connected to WiFi
- Check Home Assistant logs for errors

**AC not responding:**
- Verify AC unit is online in Bluestar app
- Check network connectivity
- Try restarting the integration

**Temperature not updating:**
- Integration updates every 30 seconds
- Check AC unit's temperature sensor
- Verify AC unit is reporting correctly

### Debug Logging
Add to `configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.bluestar_ac: debug
```

## 📊 Supported Features

- ✅ Power On/Off
- ✅ Mode Selection (Fan, Cool, Dry, Auto)
- ✅ Temperature Control (16°C - 30°C)
- ✅ Fan Speed Control (Low, Med, High, Turbo, Auto)
- ✅ Swing Control (Off, 15°, 30°, 45°, 60°, Auto)
- ✅ Display Control (On/Off)
- ✅ Real-time Status Updates
- ✅ Device Discovery
- ✅ Error Recovery

## 🆘 Support

- **GitHub Issues**: https://github.com/sankarhansdah/bluestar-ha-v3/issues
- **Documentation**: https://github.com/sankarhansdah/bluestar-ha-v3/blob/main/README.md
- **Home Assistant Community**: https://community.home-assistant.io/

## 📝 Notes

- This integration is based on reverse engineering of the Bluestar Android app
- Uses the same proven methods as our working web application
- All previous SSL, MQTT, and API issues have been resolved
- Production-ready with comprehensive error handling

---

**Version**: 3.0.0  
**Last Updated**: September 2025  
**Compatibility**: Home Assistant 2023.1.0+


