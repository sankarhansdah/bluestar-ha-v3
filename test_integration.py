#!/usr/bin/env python3
"""Test script for Bluestar HA integration."""

import asyncio
import logging
import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

from bluestar_ac.api import BluestarAPI, BluestarAPIError

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_integration():
    """Test the Bluestar integration."""
    logger.info("🧪 Starting Bluestar HA Integration Test")
    
    # Test credentials (replace with your actual credentials)
    phone = "9439614598"  # Replace with your phone number
    password = "Sonu@blue4"  # Replace with your password
    
    try:
        # Create API client
        logger.info("📡 Creating API client")
        api = BluestarAPI(phone=phone, password=password)
        
        # Test login
        logger.info("🔐 Testing login")
        await api.async_login()
        logger.info("✅ Login successful")
        
        # Test device fetch
        logger.info("📱 Fetching devices")
        devices = await api.async_get_devices()
        logger.info(f"✅ Found {len(devices)} devices")
        
        # Display device information
        for device in devices:
            logger.info(f"Device: {device['name']} (ID: {device['id']})")
            logger.info(f"  Connected: {device['connected']}")
            logger.info(f"  State: {device['state']}")
        
        # Test control command (if devices available)
        if devices:
            device_id = devices[0]['id']
            logger.info(f"🎛️ Testing control command on device {device_id}")
            
            # Test power toggle
            current_power = devices[0]['state'].get('power', False)
            new_power = not current_power
            
            control_data = {"pow": 1 if new_power else 0}
            result = await api.async_control_device(device_id, control_data)
            logger.info(f"✅ Control command successful: {result}")
        
        # Close API client
        await api.async_close()
        logger.info("🔌 API client closed")
        
        logger.info("🎉 All tests passed!")
        return True
        
    except BluestarAPIError as e:
        logger.error(f"❌ Bluestar API Error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)


