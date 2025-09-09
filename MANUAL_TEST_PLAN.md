# Bluestar Smart AC - 10-Step Manual Test Plan

## Prerequisites
- Home Assistant running and accessible
- Bluestar AC credentials (phone number and password)
- AC device powered on and connected to WiFi
- Terminal access to Home Assistant

## Step 1: Install Integration
1. **Copy Integration Files**
   ```bash
   # In Home Assistant Terminal
   cd /config
   wget https://raw.githubusercontent.com/sankarhansdah/bluestar-ha-v3/main/install.sh
   chmod +x install.sh
   ./install.sh
   ```

2. **Restart Home Assistant**
   - Go to Settings → System → Restart
   - Wait for restart to complete

3. **Verify Installation**
   ```bash
   # Check logs for successful loading
   ha core logs | grep -E "(bluestar_ac|B1|B2|B3)"
   ```

**Expected Result**: Integration loads without errors, breadcrumb logs B1-B3 appear

---

## Step 2: Add Integration via UI
1. **Navigate to Integrations**
   - Go to Settings → Devices & Services
   - Click "Add Integration"

2. **Search for Bluestar**
   - Type "Bluestar" in search box
   - Select "Bluestar Smart AC (Unofficial)"

3. **Enter Credentials**
   - Phone Number: `9439614598` (or your phone)
   - Password: `Sonu@blue4` (or your password)
   - Click "Submit"

4. **Verify Success**
   - Should see "Successfully created Bluestar AC (9439614598)"
   - Integration appears in Devices & Services list

**Expected Result**: Integration added successfully, no error messages

---

## Step 3: Verify Device Discovery
1. **Check Devices List**
   - Go to Settings → Devices & Services → Devices
   - Look for "Bluestar AC" device

2. **Verify Device Info**
   - Device name: "Bluestar AC" (or custom name)
   - Manufacturer: "Bluestar"
   - Model: "Smart AC"

3. **Check Entities**
   - Click on the device
   - Should see multiple entities:
     - Climate entity (main AC control)
     - Display switch
     - Signal strength sensor
     - Error code sensor
     - Connection status sensor
     - Vertical swing select
     - Horizontal swing select
     - Force sync button

**Expected Result**: Device and all entities appear correctly

---

## Step 4: Test Climate Entity
1. **Navigate to Climate**
   - Go to Overview → Climate
   - Find "Bluestar AC" climate entity

2. **Check Current State**
   - Verify current temperature is displayed
   - Check if AC is ON/OFF
   - Verify current mode (Cool/Dry/Fan/Auto)

3. **Test Power Control**
   - Click power button to turn ON
   - Wait 3-5 seconds
   - Verify AC turns on (check physical AC)
   - Click power button to turn OFF
   - Wait 3-5 seconds
   - Verify AC turns off

**Expected Result**: Power control works, state updates within 5 seconds

---

## Step 5: Test Temperature Control
1. **Set Target Temperature**
   - Use temperature slider or +/- buttons
   - Set temperature to 22°C
   - Wait 3-5 seconds

2. **Verify Change**
   - Check physical AC display
   - Verify target temperature changed
   - Check Home Assistant shows new temperature

3. **Test Range Limits**
   - Try to set temperature below 16°C (should limit to 16°C)
   - Try to set temperature above 30°C (should limit to 30°C)

**Expected Result**: Temperature control works, limits enforced

---

## Step 6: Test HVAC Modes
1. **Test Mode Changes**
   - Click mode dropdown
   - Select "Cool" mode
   - Wait 3-5 seconds
   - Verify AC switches to Cool mode

2. **Test All Modes**
   - Switch to "Dry" mode
   - Switch to "Fan Only" mode
   - Switch to "Auto" mode
   - Verify each mode change works

3. **Test Mode + Power**
   - Turn AC OFF
   - Try to change mode
   - Verify mode doesn't change when OFF

**Expected Result**: All HVAC modes work correctly

---

## Step 7: Test Fan Speed Control
1. **Access Fan Controls**
   - In climate entity, find fan speed dropdown
   - Should show: Low, Medium, High, Turbo, Auto

2. **Test Fan Speeds**
   - Select "Low" fan speed
   - Wait 3-5 seconds
   - Verify AC fan speed changes
   - Test "Medium", "High", "Turbo" speeds

3. **Test Auto Fan**
   - Select "Auto" fan speed
   - Verify AC switches to auto fan mode

**Expected Result**: All fan speeds work correctly

---

## Step 8: Test Swing Controls
1. **Test Vertical Swing**
   - Go to device page
   - Find "Vertical Swing" select entity
   - Change from "Off" to "Auto"
   - Wait 3-5 seconds
   - Verify AC vertical swing activates

2. **Test Horizontal Swing**
   - Find "Horizontal Swing" select entity
   - Change from "Off" to "30°"
   - Wait 3-5 seconds
   - Verify AC horizontal swing changes

3. **Test Swing Angles**
   - Try different angles: 15°, 30°, 45°, 60°
   - Verify each angle works correctly

**Expected Result**: Both swing controls work with all angles

---

## Step 9: Test Switch and Sensors
1. **Test Display Switch**
   - Find "Display" switch entity
   - Turn OFF display
   - Wait 3-5 seconds
   - Verify AC display turns off
   - Turn ON display
   - Verify AC display turns on

2. **Check Sensors**
   - Signal Strength sensor: Should show RSSI value (e.g., -45 dBm)
   - Error Code sensor: Should show 0 (no errors)
   - Connection Status sensor: Should show "Connected"

3. **Test Force Sync Button**
   - Find "Force Sync" button entity
   - Click the button
   - Check logs for sync activity

**Expected Result**: All switches and sensors work correctly

---

## Step 10: Test Real-time Updates
1. **Enable Debug Logging**
   ```bash
   # Add to configuration.yaml
   logger:
     default: warning
     logs:
       custom_components.bluestar_ac: debug
   ```

2. **Monitor Logs**
   ```bash
   # Watch for breadcrumb logs
   ha core logs --follow | grep -E "(B1|B2|B3|CL1|CL2|SW1|SW2|SE1|SE2)"
   ```

3. **Test Live Updates**
   - Change AC settings from physical remote
   - Wait 30 seconds (polling interval)
   - Verify Home Assistant updates automatically
   - Check logs for data updates (C1, C2, C3)

4. **Test MQTT Updates**
   - If MQTT is working, changes should appear within 3 seconds
   - Look for MQTT logs (API19-API28)

**Expected Result**: Real-time updates work, logs show proper breadcrumbs

---

## Troubleshooting Checklist

### If Integration Won't Load
- Check logs for import errors
- Verify all files are in correct location
- Restart Home Assistant completely

### If Login Fails
- Verify phone number format (no spaces, country code)
- Check password is correct
- Test credentials in webapp first

### If Device Not Found
- Verify AC is powered on and connected to WiFi
- Check AC is registered in Bluestar app
- Wait 5 minutes for device discovery

### If Controls Don't Work
- Check AC is online (green indicator in app)
- Verify MQTT connection in logs
- Try force sync button
- Check for error codes in sensors

### If Updates Are Slow
- MQTT may be disconnected, using HTTP fallback
- Check network connectivity
- Verify AWS IoT endpoint is accessible

## Success Criteria
✅ All 10 steps complete without errors  
✅ AC responds to all controls within 5 seconds  
✅ Real-time updates work (within 30 seconds polling)  
✅ All entities show correct states  
✅ No error messages in logs  
✅ Physical AC matches Home Assistant state  

## Performance Benchmarks
- **Login**: < 5 seconds
- **Device Discovery**: < 10 seconds  
- **Control Response**: < 5 seconds (MQTT) / < 15 seconds (HTTP)
- **State Updates**: < 30 seconds (polling) / < 3 seconds (MQTT)
- **Error Recovery**: Automatic reconnection within 60 seconds
