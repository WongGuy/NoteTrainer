# Configuration
SAMPLERATE = 48000  # Hz
BUFFER_SIZE = 1024*4
HOP_SIZE = BUFFER_SIZE // 4
BLOCKSIZE = HOP_SIZE
TOTAL_INPUT_CHANNELS = 6
TARGET_CHANNEL = 2  # 0-indexed
SILENCE = 48  # dB
MIN_FREQUENCY = 60  # Hz
MAX_FREQUENCY = 2000  # Hz
DEVICE_NAME = "Focusrite USB ASIO"
A4 = 440.0  # Frequency of A4 in Hz
NOTE_NAMES_ALL = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
NOTE_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTE_NAMES_SHARP_AND_FLAT = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
SHARPS_ENABLED = True
FLATS_ENABLED = True
QUEUE_SIZE = 5
PAUSE_TIME_SECONDS = 15