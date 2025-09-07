# Bluestar Smart AC Home Assistant Integration v3.0 - Complete Implementation

## 🎯 Project Summary

This is a complete, production-ready Home Assistant integration for Bluestar Smart AC units, built using the proven methods from our working web application. The integration provides full control of AC units through Home Assistant's native interface.

## 🏗️ Architecture Overview

### Based on Working Webapp Methods
- **Exact MQTT Implementation**: Uses the same MQTT client from our working webapp
- **Multi-step Control Algorithm**: MQTT primary, HTTP fallback, force sync
- **API Compatibility**: 100% compatible with original Bluestar app
- **Error Handling**: Comprehensive error management and recovery

### Home Assistant Integration Structure
```
bluestar-ha-v3/
├── custom_components/
│   └── bluestar_ac/
│       ├── __init__.py          # Main integration setup
│       ├── api.py              # API client (from webapp)
│       ├── climate.py          # Climate platform
│       ├── config_flow.py      # Configuration flow
│       ├── coordinator.py      # Data update coordinator
│       ├── const.py            # Constants and configuration
│       ├── manifest.json       # Integration manifest
│       └── strings.json        # UI strings
├── hacs.json                   # HACS configuration
├── README.md                   # Comprehensive documentation
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── install.sh                  # Installation script
└── test_integration.py         # Test script
```

## ✨ Features

### Complete AC Control
- **Power Control**: Turn AC units on/off
- **Mode Selection**: Fan, Cool, Dry, Auto modes
- **Temperature Control**: Set target temperature (16°C - 30°C)
- **Fan Speed Control**: Low, Medium, High, Turbo, Auto speeds
- **Swing Control**: Vertical swing with 6 positions (Off, 15°, 30°, 45°, 60°, Auto)
- **Display Control**: Control AC display on/off

### Advanced Features
- **Real-time Status**: Live monitoring every 30 seconds
- **Device Discovery**: Automatic discovery of all AC units
- **Auto-reconnection**: Automatic reconnection on network issues
- **Error Recovery**: Comprehensive error handling and logging
- **Home Assistant Native**: Full integration with HA's climate platform

## 🔧 Technical Implementation

### API Client (`api.py`)
- **BluestarAPI**: Main API client with login and device management
- **BluestarMQTTClient**: MQTT client for real-time control
- **Multi-step Control**: Primary MQTT, HTTP fallback, force sync
- **Thread-safe SSL**: Proper SSL context handling for MQTT

### Climate Platform (`climate.py`)
- **BluestarClimateEntity**: Full climate entity implementation
- **All HVAC Modes**: Fan, Cool, Dry, Auto
- **Temperature Control**: Precise temperature setting
- **Fan Speed Control**: All fan speed options
- **Swing Control**: Complete swing functionality

### Data Coordinator (`coordinator.py`)
- **BluestarDataUpdateCoordinator**: Manages data updates
- **30-second Updates**: Regular status refresh
- **Error Handling**: Comprehensive error management
- **Device Processing**: Converts API data to HA format

### Configuration Flow (`config_flow.py`)
- **User-friendly Setup**: Easy credential entry
- **Validation**: Tests credentials during setup
- **Error Messages**: Clear error reporting
- **HACS Compatible**: Works with HACS installation

## 🚀 Installation Methods

### Method 1: HACS (Recommended)
1. Install HACS if not already installed
2. Add custom repository: `https://github.com/sankarhansdah/bluestar-ha-v3`
3. Install "Bluestar Smart AC" integration
4. Restart Home Assistant
5. Add integration via Settings → Devices & Services

### Method 2: Manual Installation
1. Download the integration files
2. Copy to `custom_components/bluestar_ac/`
3. Restart Home Assistant
4. Add integration via Settings → Devices & Services

### Method 3: Installation Script
1. Run `./install.sh` from the integration directory
2. Follow the prompts
3. Restart Home Assistant
4. Add integration via Settings → Devices & Services

## ⚙️ Configuration

### Required Credentials
- **Phone Number**: Your Bluestar account phone number
- **Password**: Your Bluestar account password

### Optional Settings
- **API Base URL**: `https://api.bluestarindia.com/prod` (default)
- **MQTT Endpoint**: `a1b2c3d4e5f6g7-ats.iot.ap-south-1.amazonaws.com` (default)

### Setup Process
1. Go to Settings → Devices & Services
2. Click Add Integration
3. Search for "Bluestar Smart AC"
4. Enter your credentials
5. The integration will discover your AC units
6. Complete the setup

## 🎛️ Usage Examples

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
```

### Lovelace Card
```yaml
type: thermostat
entity: climate.bluestar_ac_living_room
name: Living Room AC
```

## 🧪 Testing

### Test Script
Run the included test script to validate the integration:

```bash
python3 test_integration.py
```

The test script will:
- Test API login
- Fetch devices
- Test control commands
- Validate MQTT connection

### Debug Logging
Enable debug logging in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.bluestar_ac: debug
```

## 🔍 Troubleshooting

### Common Issues

**Integration won't load:**
- Check credentials are correct
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

### Log Analysis
Look for these log patterns:
- `✅ MQTT Connected`: MQTT connection successful
- `✅ Successfully logged in`: API authentication successful
- `📤 MQTT Publishing`: Control commands being sent
- `❌ MQTT Connection error`: Connection issues

## 📊 Supported Devices

This integration supports all Bluestar Smart AC units that work with the official Bluestar mobile app:

- Bluestar Smart AC models with WiFi connectivity
- All AC units registered in your Bluestar account
- Units with MQTT and HTTP API support

## 🔄 Updates

- **HACS**: Automatic updates when installed via HACS
- **Manual**: Download latest release and replace files
- **Version**: Currently v3.0.0

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This is an unofficial integration created through reverse engineering. Use at your own risk.

## 🙏 Acknowledgments

- Based on successful reverse engineering of Bluestar Android app
- Built using proven methods from our working web application
- Inspired by the Home Assistant community

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: README.md

---

**Version**: 3.0.0  
**Last Updated**: September 2025  
**Compatibility**: Home Assistant 2023.1.0+  
**Status**: ✅ Complete & Ready for Production
