import os
# Set environment variable for ASIO, MUST GO BEFORE IMPORTING SOUNDDEVICE
os.environ["SD_ENABLE_ASIO"] = "1"

import aubio
import numpy as np
import sounddevice as sd

# Stream configuration
SAMPLERATE = 44100  # Hz
BUFFER_SIZE = 4096  # Larger buffer size
HOP_SIZE = BUFFER_SIZE // 4  # Common practice to set hop size to a fraction of buffer size
BLOCKSIZE = HOP_SIZE
TOTAL_INPUT_CHANNELS = 6  # Total input channels on the audio interface
TARGET_CHANNEL = 2  # Change this to select a specific input channel (0-indexed)
SILENCE = 36  # Silence threshold in dB 
MIN_FREQUENCY = 60  # Hz
MAX_FREQUENCY = 2000  # Hz


# Function to find device ID by name
def find_device_id(device_name):
    try:
        devices = sd.query_devices()  # Get all audio devices
        for idx, device in enumerate(devices):
            if device_name in device['name']:
                return idx, device['name']  # Return both ID and name
        raise ValueError(f"Device '{device_name}' not found.")
    except Exception as e:
        print(f"Error querying devices: {e}")
        return None

# Define the target device name
DEVICE_NAME = "Focusrite USB ASIO"

# Find device ID
device_id, device_text_name = find_device_id(DEVICE_NAME)
if device_id is None:
    print("Device not found. Exiting...")
    raise SystemExit("Device not found. Exiting...")



try:
    # Initialize Aubio pitch detector
    pitch_detector = aubio.pitch("yin", BUFFER_SIZE, HOP_SIZE, SAMPLERATE)
    pitch_detector.set_unit("Hz")
    pitch_detector.set_silence(-SILENCE) 
    
    device_info = sd.query_devices(device_id)
    actual_samplerate = device_info['default_samplerate']
    print(f"Actual device sample rate: {actual_samplerate} Hz")
    print(f"Assumed device sample rate: {SAMPLERATE} Hz")

    print("Aubio pitch detector initialized successfully.")
except Exception as e:
    print(f"Error initializing Aubio pitch detector: {e}")

def frequency_to_note_name(freq):
    A4 = 440.0  # Frequency of A4 in Hz
    if freq <= 0:
        return "Silence"
    
    # Calculate MIDI note number based on frequency
    midi_note = 69 + 12 * np.log2(freq / A4)
    
    # Round to the nearest whole MIDI note
    rounded_midi_note = int(np.round(midi_note))
    
    # Map MIDI note to note name
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = rounded_midi_note // 12 - 1
    note = note_names[rounded_midi_note % 12]
    
    # Calculate the frequency of the rounded note
    rounded_freq = A4 * 2**((rounded_midi_note - 69) / 12)
    
    # Optionally return the difference from the note center in cents
    cents_difference = int(1200 * np.log2(freq / rounded_freq))
    
    return note, octave, cents_difference

previous_note = None
previous_octave = None
previous_state = "silence"
consecutive_count = 0

# Define the audio callback function
def audio_callback(indata, frames, time, status):
    global previous_note, previous_octave, previous_state, consecutive_count

    if status:
        print("Status:", status)
    
    # Access the desired channel
    selected_channel_data = indata[:, TARGET_CHANNEL]
    
    # Convert audio data to pitch
    pitch = pitch_detector(selected_channel_data.astype(np.float32))[0]
    
    if pitch > MIN_FREQUENCY and pitch < MAX_FREQUENCY:  # When a pitch is detected
        note, octave, cents_difference = frequency_to_note_name(pitch)
        current_state = f"{note}{octave}"
        
        if current_state == previous_state:
            # Increment the counter if the same note is detected
            consecutive_count += 1
        else:
            # Reset the counter if a different note is detected
            consecutive_count = 1
            previous_state = current_state
        
        # Print only if the same note is detected for 5 consecutive samples
        if consecutive_count == 3:
            print(f"Detected note: {note}{octave} ({pitch:.2f} Hz) ({cents_difference})")
    else:  # Silence detected
        current_state = "silence"
        consecutive_count = 0  # Reset the counter during silence

# Create the InputStream
try:
    stream = sd.InputStream(
        device=device_id,
        callback=audio_callback,
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=TOTAL_INPUT_CHANNELS  # Number of input channels to read
    )
    print(f"Using device ID: {device_id}, Device Name: {device_text_name}")
except Exception as e:
    print(f"Error initializing stream: {e}")

try:
    with stream:  # Automatically manage the stream's lifecycle
        print("Press Ctrl+C to stop the audio stream.")
        while True:
            sd.sleep(100)  # Sleep for a short period to keep the loop running
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Stopping the audio stream...")
