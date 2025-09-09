# Bluestar Smart AC Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/sankarhansdah/bluestar-ha-v3.svg)](https://github.com/sankarhansdah/bluestar-ha-v3/releases)
[![GitHub stars](https://img.shields.io/github/stars/sankarhansdah/bluestar-ha-v3.svg)](https://github.com/sankarhansdah/bluestar-ha-v3/stargazers)

A comprehensive Home Assistant integration for Bluestar Smart AC units, providing full control and monitoring capabilities through both MQTT and HTTP APIs.

## ✨ Features

### 🎛️ Complete AC Control
- **Power Control**: Turn AC on/off
- **Temperature Control**: Set target temperature (16-30°C)
- **HVAC Modes**: Cool, Dry, Fan Only, Auto
- **Fan Speed**: Low, Medium, High, Turbo, Auto
- **Swing Control**: Vertical and horizontal swing with multiple angles
- **Display Control**: Turn AC display on/off

### 📊 Monitoring & Sensors
- **Signal Strength**: RSSI monitoring
- **Error Detection**: Error code monitoring
- **Connection Status**: Online/offline status
- **Current Temperature**: Real-time temperature reading

### 🔄 Real-time Updates
- **MQTT Integration**: Instant updates via AWS IoT
- **HTTP Fallback**: Reliable polling when MQTT unavailable
- **Auto-reconnection**: Automatic recovery from network issues

### 🏠 Home Assistant Integration
- **Climate Entity**: Full climate control interface
- **Switch Entities**: Display and other controls
- **Sensor Entities**: Monitoring and diagnostics
- **Select Entities**: Swing angle controls
- **Button Entities**: Force sync functionality

## 🚀 Quick Start

### Installation via HACS (Recommended)
1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Go to HACS → Integrations
3. Click the three dots menu → Custom repositories
4. Add repository: `https://github.com/sankarhansdah/bluestar-ha-v3`
5. Search for "Bluestar Smart AC" and install
6. Restart Home Assistant

### Manual Installation
```bash
# In Home Assistant Terminal
cd /config
wget https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/install.sh
chmod +x install.sh
./install.sh
```

### Configuration
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"Bluestar Smart AC"**
4. Enter your credentials:
   - **Phone Number**: Your registered phone number
   - **Password**: Your Bluestar account password
5. Click **Submit**

## 📋 Requirements

- Home Assistant 2023.1.0 or later
- Bluestar Smart AC with WiFi connectivity
- Valid Bluestar account credentials
- Internet connection for cloud communication

## 🔧 Configuration

### Basic Configuration
The integration requires only your Bluestar account credentials:
- **Phone Number**: The phone number registered with your Bluestar account
- **Password**: Your Bluestar account password

### Advanced Configuration
You can customize the integration behavior by editing `configuration.yaml`:

```yaml
# Example configuration.yaml
logger:
  default: warning
  logs:
    custom_components.bluestar_ac: debug

bluestar_ac:
  # Optional: Override default polling interval (seconds)
  scan_interval: 30
  
  # Optional: Enable debug logging
  debug: true
```

## 🎯 Supported Devices

- **Bluestar Smart AC Units**: All WiFi-enabled Bluestar AC models
- **Protocol Support**: AWS IoT MQTT + HTTP API fallback
- **Authentication**: Phone number + password based

## 📱 Entity Types

### Climate Entity
- **Name**: `Bluestar AC`
- **Features**: Power, Temperature, Mode, Fan Speed, Swing
- **Controls**: Full climate control interface

### Switch Entities
- **Display Switch**: Control AC display on/off
- **Name**: `{Device Name} Display`

### Sensor Entities
- **Signal Strength**: RSSI in dBm
- **Error Code**: Current error status
- **Connection Status**: Online/offline status

### Select Entities
- **Vertical Swing**: Off, 15°, 30°, 45°, 60°, Auto
- **Horizontal Swing**: Off, 15°, 30°, 45°, 60°, Auto

### Button Entities
- **Force Sync**: Manual cloud synchronization

## 🔍 Troubleshooting

### Common Issues

#### Integration Won't Load
```bash
# Check logs for errors
ha core logs | grep bluestar_ac
```
**Solutions**:
- Verify all files are in `/config/custom_components/bluestar_ac/`
- Restart Home Assistant completely
- Check for Python syntax errors

#### Login Fails
**Symptoms**: "Invalid phone number or password" error
**Solutions**:
- Verify phone number format (no spaces, include country code)
- Test credentials in official Bluestar app first
- Check password is correct (case-sensitive)

#### Device Not Found
**Symptoms**: No AC device appears after login
**Solutions**:
- Ensure AC is powered on and connected to WiFi
- Verify AC is registered in Bluestar app
- Wait 5-10 minutes for device discovery
- Check AC is online (green indicator in app)

#### Controls Don't Work
**Symptoms**: Buttons/sliders don't affect AC
**Solutions**:
- Check AC is online (green indicator in app)
- Verify MQTT connection in logs
- Try force sync button
- Check for error codes in sensor entities

#### Slow Updates
**Symptoms**: Changes take >30 seconds to appear
**Solutions**:
- MQTT may be disconnected, using HTTP fallback
- Check network connectivity
- Verify AWS IoT endpoint accessibility
- Restart integration

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
# Add to configuration.yaml
logger:
  default: warning
  logs:
    custom_components.bluestar_ac: debug
```

Then check logs:
```bash
ha core logs --follow | grep -E "(B1|B2|B3|CL1|CL2|SW1|SW2|SE1|SE2)"
```

### Breadcrumb Logs

The integration uses numbered breadcrumb logs for easy debugging:

- **B1-B13**: Setup process
- **CL1-CL10**: Climate entity operations
- **SW1-SW6**: Switch entity operations
- **SE1-SE4**: Sensor entity operations
- **API1-API29**: API client operations
- **C1-C5**: Coordinator operations

## 🔄 Webapp ↔ HA Mapping

| Webapp Feature | HA Entity | Platform |
|----------------|-----------|----------|
| Power Button | Climate | climate |
| Temperature Slider | Climate | climate |
| Mode Buttons | Climate | climate |
| Fan Speed | Climate | climate |
| Vertical Swing | Vertical Swing | select |
| Horizontal Swing | Horizontal Swing | select |
| Display Toggle | Display | switch |
| Signal Strength | Signal Strength | sensor |
| Connection Status | Connection Status | sensor |
| Error Code | Error Code | sensor |
| Force Sync | Force Sync | button |

## 📊 Performance

- **Login Time**: < 5 seconds
- **Device Discovery**: < 10 seconds
- **Control Response**: < 5 seconds (MQTT) / < 15 seconds (HTTP)
- **State Updates**: < 30 seconds (polling) / < 3 seconds (MQTT)
- **Error Recovery**: Automatic reconnection within 60 seconds

## 🛠️ Development

### Architecture
- **API Client**: Async HTTP + MQTT client (`api.py`)
- **Coordinator**: Data update coordinator (`coordinator.py`)
- **Platforms**: Climate, Switch, Sensor, Select, Button entities
- **Config Flow**: Guided setup process

### Protocol
- **Authentication**: Phone + password via HTTP API
- **Device Control**: MQTT primary, HTTP fallback
- **State Updates**: AWS IoT Device Shadow
- **Real-time**: MQTT push notifications

### Testing
See [MANUAL_TEST_PLAN.md](MANUAL_TEST_PLAN.md) for comprehensive testing procedures.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sankarhansdah/bluestar-ha-v3/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sankarhansdah/bluestar-ha-v3/discussions)
- **Documentation**: [Wiki](https://github.com/sankarhansdah/bluestar-ha-v3/wiki)

## 🙏 Acknowledgments

- Based on reverse engineering of the official Bluestar Android app
- Inspired by the working webapp implementation
- Built with Home Assistant best practices
- Uses AWS IoT for real-time communication

## 📈 Changelog

### v3.0.0 (Current)
- Complete rewrite based on working webapp
- Full MQTT + HTTP API support
- All platforms implemented (Climate, Switch, Sensor, Select, Button)
- Real-time updates via AWS IoT
- Comprehensive error handling and recovery
- Extensive debug logging with breadcrumbs
- Production-ready code with proper async handling

### v2.x (Previous)
- Basic HTTP-only implementation
- Limited platform support
- Manual credential configuration
- Basic error handling

---

**Made with ❤️ for the Home Assistant community**