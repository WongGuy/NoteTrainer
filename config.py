#config.py

# Configuration
SAMPLERATE = 48000  # Hz
BUFFER_SIZE = 1024*4
HOP_SIZE = BUFFER_SIZE // 4
BLOCKSIZE = HOP_SIZE
MIN_FREQUENCY = 60  # Hz
MAX_FREQUENCY = 2000  # Hz
NOTE_NAMES_ALL = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
NOTE_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_NAMES_SHARP_ONLY = ['C#', 'D#', 'F#', 'G#', 'A#']
NOTE_NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NOTE_NAMES_FLAT_ONLY = ['Db', 'Eb', 'Gb', 'Ab', 'Bb']
NOTE_NAMES_NATURAL_ONLY = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
NOTE_NAMES_SHARP_AND_FLAT = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
QUEUE_SIZE = 4
PAUSE_TIME_SECONDS = 15