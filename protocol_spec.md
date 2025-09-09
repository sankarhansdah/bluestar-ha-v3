# Bluestar Smart AC Protocol Specification

## Overview
This document defines the complete communication protocol for Bluestar Smart AC devices, extracted from the working webapp implementation.

## Authentication Flow

### Login Request
- **Endpoint**: `POST https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod/auth/login`
- **Headers**:
  ```
  Content-Type: application/json
  X-APP-VER: v4.11.4-133
  X-OS-NAME: Android
  X-OS-VER: v13-33
  User-Agent: com.bluestarindia.bluesmart
  ```
- **Request Body**:
  ```json
  {
    "auth_id": "9439614598",  // Phone number
    "auth_type": 1,           // 1 = phone, 2 = email
    "password": "Sonu@blue4"
  }
  ```

### Login Response
- **Success Response**:
  ```json
  {
    "session": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user123",
      "name": "User Name"
    },
    "mi": "ZW5kcG9pbnQ6OmFjY2Vzc0tleTo6c2VjcmV0S2V5"  // Base64 encoded AWS credentials
  }
  ```

### Credential Extraction
The `mi` field contains Base64-encoded AWS IoT credentials:
- **Format**: `endpoint::accessKey::secretKey`
- **Decode**: `Buffer.from(mi, 'base64').toString('utf-8')`
- **Split**: `decoded.split('::')` → `[endpoint, accessKey, secretKey]`

## HTTP API Endpoints

### Device List
- **Endpoint**: `GET https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod/things`
- **Headers**:
  ```
  X-APP-VER: v4.11.4-133
  X-OS-NAME: Android
  X-OS-VER: v13-33
  User-Agent: com.bluestarindia.bluesmart
  Content-Type: application/json
  X-APP-SESSION: {session_token}
  ```

### Device Control (HTTP Fallback)
- **Endpoint**: `POST https://n3on22cp53.execute-api.ap-south-1.amazonaws.com/prod/things/{device_id}/preferences`
- **Headers**: Same as device list + session token
- **Request Body**:
  ```json
  {
    "preferences": {
      "mode": {
        "2": {  // Mode number as string key
          "power": "1",
          "mode": "2",
          "stemp": "24",
          "fspd": "2",
          "vswing": "0",
          "hswing": "0",
          "display": "1"
        }
      }
    }
  }
  ```

## MQTT Protocol

### Connection Configuration
- **Broker**: AWS IoT Core (endpoint from `mi` field)
- **Protocol**: WSS (WebSocket Secure)
- **Port**: 443
- **Region**: ap-south-1
- **Client ID**: `u-{session_id}`
- **Keep Alive**: 30 seconds
- **Reconnect Period**: 1000ms
- **Connect Timeout**: 30 seconds

### MQTT Topics

#### State Update (Primary Control Method)
- **Topic**: `$aws/things/{device_id}/shadow/update`
- **QoS**: 0
- **Payload Structure**:
  ```json
  {
    "state": {
      "desired": {
        "pow": 1,           // Power: 0=off, 1=on
        "mode": {           // Mode: nested object
          "value": 2        // 0=fan, 2=cool, 3=dry, 4=auto
        },
        "stemp": "24",      // Set temperature (string)
        "fspd": 2,          // Fan speed: 2=low, 3=med, 4=high, 6=turbo, 7=auto
        "vswing": 0,        // Vertical swing: 0=off, 1-4=angles, -1=auto
        "hswing": 0,        // Horizontal swing: 0=off, 1-4=angles, -1=auto
        "display": 1,       // Display: 0=off, 1=on
        "ts": 1640995200000, // Timestamp
        "src": "anmq"       // Source identifier
      }
    }
  }
  ```

#### Force Sync
- **Topic**: `things/{device_id}/control`
- **QoS**: 0
- **Payload**:
  ```json
  {
    "fpsh": 1
  }
  ```

### Device State Response
- **Format**: AWS IoT Device Shadow
- **Sample Response**:
  ```json
  {
    "state": {
      "pow": 1,             // Power status
      "mode": 2,            // Current mode
      "stemp": "24",        // Set temperature
      "ctemp": "27.5",      // Current temperature
      "fspd": 2,            // Fan speed
      "vswing": 0,          // Vertical swing
      "hswing": 0,          // Horizontal swing
      "display": 1,         // Display status
      "rssi": -45,          // Signal strength
      "err": 0,             // Error code
      "src": "device"       // Source
    },
    "connected": true,      // Device online status
    "timestamp": 1640995200000
  }
  ```

## Control Parameters

### Power Control
- **Parameter**: `pow`
- **Values**: `0` = OFF, `1` = ON

### HVAC Modes
- **Parameter**: `mode.value`
- **Values**:
  - `0` = Fan Only
  - `2` = Cool
  - `3` = Dry
  - `4` = Auto

### Temperature
- **Parameter**: `stemp`
- **Range**: 16-30°C
- **Format**: String (e.g., "24")

### Fan Speed
- **Parameter**: `fspd`
- **Values**:
  - `2` = Low
  - `3` = Medium
  - `4` = High
  - `6` = Turbo
  - `7` = Auto

### Swing Control
- **Vertical Swing**: `vswing`
- **Horizontal Swing**: `hswing`
- **Values**:
  - `0` = Off
  - `1` = 15°
  - `2` = 30°
  - `3` = 45°
  - `4` = 60°
  - `-1` = Auto

### Display Control
- **Parameter**: `display`
- **Values**: `0` = Off, `1` = On

## Timing Expectations

### Polling Intervals
- **Device Status**: 5 seconds (webapp)
- **HA Integration**: 30 seconds (recommended)

### MQTT Keepalive
- **Interval**: 30 seconds
- **Reconnect Backoff**: 1000ms initial, exponential backoff

### Command Response Time
- **MQTT**: ≤3 seconds
- **HTTP Fallback**: ≤15 seconds

## Error Handling

### Common Error Codes
- **401**: Invalid session token
- **403**: Insufficient permissions
- **404**: Device not found
- **500**: Server error

### MQTT Error Handling
- **Connection Timeout**: 30 seconds
- **Auto-reconnect**: Enabled with exponential backoff
- **Fallback**: HTTP API when MQTT unavailable

## Security Considerations

### Session Management
- **Token TTL**: Not specified (assume 24 hours)
- **Refresh**: Re-login required on token expiry

### Credential Security
- **AWS Credentials**: Extracted from login response
- **Storage**: Secure storage required
- **Transmission**: HTTPS/WSS only

## TODOs and Ambiguities

1. **Session Token TTL**: Exact expiration time unknown - assume 24 hours
2. **Device Discovery**: Only one device ID hardcoded (`24587ca091f8`)
3. **Error Codes**: Complete error code mapping not available
4. **Rate Limiting**: API rate limits not documented
5. **Multi-device**: Support for multiple ACs not tested

## Default Values

### Safe Defaults
- **Temperature**: 24°C
- **Mode**: Cool (2)
- **Fan Speed**: Low (2)
- **Swing**: Off (0)
- **Display**: On (1)
- **Power**: Off (0)
