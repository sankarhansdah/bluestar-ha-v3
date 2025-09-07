# Bluestar Smart AC - Home Assistant Integration v3.0

A complete Home Assistant integration for Bluestar Smart AC units, built using the proven methods from our working webapp implementation.

## 🎯 Overview

This integration provides full control of your Bluestar Smart AC units through Home Assistant, using the exact same control mechanisms that were reverse-engineered from the original Android app and successfully implemented in our web application.

## ✨ Features

### Complete AC Control
- **Power Control**: Turn AC units on/off
- **Mode Selection**: Fan, Cool, Dry, Auto modes
- **Temperature Control**: Set target temperature (16°C - 30°C)
- **Fan Speed Control**: Low, Medium, High, Turbo, Auto speeds
- **Swing Control**: Vertical swing with 6 positions (Off, 15°, 30°, 45°, 60°, Auto)
- **Display Control**: Control AC display on/off

### Advanced Features
- **Real-time Status**: Live monitoring of AC state
- **Multi-step Control Algorithm**: MQTT primary, HTTP fallback, force sync
- **Auto-reconnection**: Automatic reconnection on network issues
- **Error Handling**: Comprehensive error management and logging
- **Device Discovery**: Automatic discovery of all AC units

## 🚀 Installation

### Method 1: HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Go to HACS → Integrations
3. Click the three dots menu → Custom repositories
4. Add this repository: `https://github.com/sankarhansdah/bluestar-ha-v3`
5. Select "Integration" as the category
6. Click "Add"
7. Find "Bluestar Smart AC" in the list and install it
8. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [releases page](https://github.com/sankarhansdah/bluestar-ha-v3/releases)
2. Extract the `bluestar_ac` folder to your `custom_components` directory
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Bluestar Smart AC" and add it

## ⚙️ Configuration

### Step 1: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Bluestar Smart AC"**
4. Click on it to start the configuration

### Step 2: Enter Credentials

Fill in the configuration form:

- **Phone Number**: Your Bluestar account phone number
- **Password**: Your Bluestar account password
- **API Base URL**: `https://api.bluestarindia.com/prod` (default)
- **MQTT Endpoint**: `a1b2c3d4e5f6g7-ats.iot.ap-south-1.amazonaws.com` (default)

### Step 3: Complete Setup

1. Click **Submit** to test the connection
2. The integration will automatically discover your AC units
3. Click **Finish** to complete the setup

## 🎛️ Usage

### Climate Entities

Each AC unit will appear as a climate entity in Home Assistant with the following controls:

- **Power**: Turn the AC on/off
- **Mode**: Select HVAC mode (Fan, Cool, Dry, Auto)
- **Temperature**: Set target temperature
- **Fan Speed**: Control fan speed
- **Swing**: Control vertical swing position

### Automation Examples

```yaml
# Turn on AC when temperature is high
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

# Turn off AC when leaving home
automation:
  - alias: "Turn off AC when leaving"
    trigger:
      - platform: state
        entity_id: person.you
        to: "not_home"
    action:
      - service: climate.turn_off
        target:
          entity_id: climate.bluestar_ac_living_room
```

### Lovelace Card Example

```yaml
type: thermostat
entity: climate.bluestar_ac_living_room
name: Living Room AC
```

## 🔧 Technical Details

### Control Algorithm

This integration uses the same multi-step control algorithm from our working webapp:

1. **Primary Method**: MQTT Shadow Updates to AWS IoT
2. **Fallback Method**: HTTP API with nested mode preferences
3. **Force Sync**: Ensures device state synchronization

### API Compatibility

- **100% Compatible**: Uses exact same API calls as the original Bluestar app
- **Real-time Updates**: Live status monitoring every 30 seconds
- **Error Recovery**: Automatic retry and fallback mechanisms

### MQTT Integration

- **Protocol**: MQTT over TLS (mqtts://)
- **Authentication**: AWS IoT credentials
- **Topics**: 
  - Control: `things/{device_id}/control`
  - Shadow Update: `$aws/things/{device_id}/shadow/update`

## 📊 Supported Devices

This integration supports all Bluestar Smart AC units that work with the official Bluestar mobile app, including:

- Bluestar Smart AC models with WiFi connectivity
- All AC units registered in your Bluestar account
- Units with MQTT and HTTP API support

## 🐛 Troubleshooting

### Common Issues

**Integration won't load:**
- Check your credentials are correct
- Ensure your AC units are connected to WiFi
- Check Home Assistant logs for error details

**AC not responding:**
- Verify your AC unit is online in the Bluestar app
- Check network connectivity
- Try restarting the integration

**Temperature not updating:**
- The integration updates every 30 seconds
- Check if the AC unit is reporting temperature correctly
- Verify the AC unit's temperature sensor is working

### Debug Logging

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.bluestar_ac: debug
```

### Log Analysis

Look for these log patterns:

- `✅ MQTT Connected`: MQTT connection successful
- `✅ Successfully logged in`: API authentication successful
- `📤 MQTT Publishing`: Control commands being sent
- `❌ MQTT Connection error`: Connection issues

## 🔄 Updates

The integration automatically checks for updates when installed via HACS. For manual installations, download the latest release and replace the files.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an unofficial integration created through reverse engineering. Use at your own risk. The authors are not responsible for any issues that may arise from using this software.

## 🙏 Acknowledgments

- Based on the successful reverse engineering of the Bluestar Android app
- Built using proven methods from our working web application
- Inspired by the Home Assistant community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sankarhansdah/bluestar-ha-v3/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sankarhansdah/bluestar-ha-v3/discussions)

---

**Version**: 3.0.0  
**Last Updated**: September 2025  
**Compatibility**: Home Assistant 2023.1.0+
