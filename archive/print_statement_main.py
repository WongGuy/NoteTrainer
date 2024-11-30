import os
# Set environment variable for ASIO, MUST GO BEFORE IMPORTING SOUNDDEVICE
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd
from note_detector import NoteDetector
from audio_device import find_device_id, get_device_info

# Configuration
SAMPLERATE = 44100  # Hz
BUFFER_SIZE = 4096
HOP_SIZE = BUFFER_SIZE // 4
BLOCKSIZE = HOP_SIZE
TOTAL_INPUT_CHANNELS = 6
TARGET_CHANNEL = 2  # 0-indexed
SILENCE = 36  # dB
MIN_FREQUENCY = 60  # Hz
MAX_FREQUENCY = 2000  # Hz
DEVICE_NAME = "Focusrite USB ASIO"

# Find device ID
device_id, device_text_name = find_device_id(DEVICE_NAME)
if device_id is None:
    print("Device not found. Exiting...")
    raise SystemExit("Device not found. Exiting...")

# Get device info
device_info = get_device_info(device_id)
actual_samplerate = device_info['default_samplerate']
print(f"Actual device sample rate: {actual_samplerate} Hz")
print(f"Assumed device sample rate: {SAMPLERATE} Hz")

# Initialize NoteDetector
note_detector = NoteDetector(
    buffer_size=BUFFER_SIZE,
    hop_size=HOP_SIZE,
    samplerate=SAMPLERATE,
    silence_threshold=SILENCE,
    min_freq=MIN_FREQUENCY,
    max_freq=MAX_FREQUENCY,
    target_channel=TARGET_CHANNEL
)

# Define the audio callback function
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    note_detector.process_audio_block(indata)

# Create and start the InputStream
try:
    stream = sd.InputStream(
        device=device_id,
        callback=audio_callback,
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=TOTAL_INPUT_CHANNELS
    )
    print(f"Using device ID: {device_id}, Device Name: {device_text_name}")
except Exception as e:
    print(f"Error initializing stream: {e}")
    raise e

try:
    with stream:
        print("Press Ctrl+C to stop the audio stream.")
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Stopping the audio stream...")
