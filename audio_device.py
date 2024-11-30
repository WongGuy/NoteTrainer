import os
# Set environment variable for ASIO, MUST GO BEFORE IMPORTING SOUNDDEVICE
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd

def find_device_id(device_name):
    """Find the device ID and name for a given device name substring."""
    try:
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device_name in device['name']:
                return idx, device['name']
        raise ValueError(f"Device '{device_name}' not found.")
    except Exception as e:
        print(f"Error querying devices: {e}")
        return None, None

def get_device_info(device_id):
    """Get device information for a given device ID."""
    try:
        device_info = sd.query_devices(device_id)
        return device_info
    except Exception as e:
        print(f"Error getting device info: {e}")
        return None
