# Bluestar Smart AC ↔ Home Assistant Mapping

## HVAC Mode Mappings

| Bluestar Mode | Bluestar Value | HA HVAC Mode | HA Value |
|---------------|----------------|--------------|----------|
| Fan Only      | 0              | fan_only     | fan_only |
| Cool          | 2              | cool         | cool     |
| Dry           | 3              | dry          | dry      |
| Auto          | 4              | auto         | auto     |
| Off           | -              | off          | off      |

## Fan Speed Mappings

| Bluestar Speed | Bluestar Value | HA Fan Mode | HA Value |
|----------------|----------------|-------------|----------|
| Low            | 2              | low         | low      |
| Medium         | 3              | medium      | medium   |
| High           | 4              | high        | high     |
| Turbo          | 6              | turbo       | turbo    |
| Auto           | 7              | auto        | auto     |

## Swing Mode Mappings

| Bluestar Swing | Bluestar Value | HA Swing Mode | HA Value |
|----------------|----------------|---------------|----------|
| Off            | 0              | off           | off      |
| 15°            | 1              | 15°           | 15°      |
| 30°            | 2              | 30°           | 30°      |
| 45°            | 3              | 45°           | 45°      |
| 60°            | 4              | 60°           | 60°      |
| Auto           | -1             | auto          | auto     |

## Temperature Mappings

| Parameter | Bluestar Field | HA Field | Range | Default |
|-----------|----------------|----------|-------|---------|
| Set Temp  | stemp          | target_temperature | 16-30°C | 24°C |
| Current   | ctemp          | current_temperature | - | - |

## Control Parameters

| Feature | Bluestar Field | HA Field | Values |
|---------|----------------|----------|--------|
| Power   | pow            | hvac_mode | 0=off, 1=on |
| Display | display        | switch    | 0=off, 1=on |
| RSSI    | rssi           | sensor    | dBm |
| Error   | err            | sensor    | error code |
| Connection | connected   | sensor    | true/false |

## MQTT Topic Mappings

| Purpose | Bluestar Topic | HA Usage |
|---------|----------------|----------|
| State Update | `$aws/things/{device_id}/shadow/update` | Primary control method |
| Force Sync | `things/{device_id}/control` | Manual sync trigger |

## Entity Mappings

| Platform | Entity Type | Purpose |
|----------|-------------|---------|
| climate  | BluestarClimateEntity | Main AC control |
| switch   | BluestarDisplaySwitch | Display on/off |
| sensor   | BluestarRSSISensor | Signal strength |
| sensor   | BluestarErrorSensor | Error codes |
| sensor   | BluestarConnectionSensor | Connection status |
| select   | BluestarVerticalSwingSelect | Vertical swing angles |
| select   | BluestarHorizontalSwingSelect | Horizontal swing angles |
| button   | BluestarForceSyncButton | Force sync with cloud |

## Feature Support Matrix

| Feature | Supported | Platform | Notes |
|---------|-----------|----------|-------|
| Power Control | ✅ | climate | Turn AC on/off |
| Temperature | ✅ | climate | Set target temperature |
| HVAC Modes | ✅ | climate | Cool, Dry, Fan, Auto |
| Fan Speed | ✅ | climate | Low, Medium, High, Turbo, Auto |
| Vertical Swing | ✅ | select | Off, 15°, 30°, 45°, 60°, Auto |
| Horizontal Swing | ✅ | select | Off, 15°, 30°, 45°, 60°, Auto |
| Display Control | ✅ | switch | Turn display on/off |
| Signal Strength | ✅ | sensor | RSSI in dBm |
| Error Monitoring | ✅ | sensor | Error codes |
| Connection Status | ✅ | sensor | Online/offline |
| Force Sync | ✅ | button | Manual cloud sync |
| MQTT Updates | ✅ | - | Real-time state updates |
| HTTP Fallback | ✅ | - | When MQTT unavailable |

## Default Values

| Parameter | Default | Notes |
|-----------|---------|-------|
| Temperature | 24°C | Safe default |
| Mode | Cool (2) | Most common mode |
| Fan Speed | Low (2) | Energy efficient |
| Vertical Swing | Off (0) | No swing |
| Horizontal Swing | Off (0) | No swing |
| Display | On (1) | Show display |
| Power | Off (0) | Start powered off |

## Error Handling

| Error Type | Handling | Fallback |
|------------|----------|----------|
| MQTT Disconnect | Auto-reconnect | HTTP API |
| HTTP Timeout | Retry with backoff | Show error |
| Invalid Credentials | Show auth error | Re-login required |
| Device Offline | Show disconnected | Continue polling |
| API Rate Limit | Exponential backoff | Reduce polling |

## Performance Characteristics

| Operation | Expected Time | Method |
|-----------|---------------|--------|
| Login | 2-5 seconds | HTTP |
| Device List | 1-3 seconds | HTTP |
| MQTT Command | <1 second | MQTT |
| HTTP Command | 2-5 seconds | HTTP |
| State Update | 5-30 seconds | Polling |
| MQTT Update | <3 seconds | Push |
