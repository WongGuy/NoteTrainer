import aubio
import numpy as np
from note_utils import *

class NoteDetector:
    def __init__(self, buffer_size, hop_size, samplerate, silence_threshold, min_freq, max_freq, target_channel):
        self.buffer_size = buffer_size
        self.hop_size = hop_size
        self.samplerate = samplerate
        self.silence_threshold = silence_threshold
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.target_channel = target_channel

        # Initialize Aubio pitch detector
        self.pitch_detector = aubio.pitch("yin", self.buffer_size, self.hop_size, self.samplerate)
        self.pitch_detector.set_unit("Hz")
        self.pitch_detector.set_silence(-self.silence_threshold)

        # State variables
        self.previous_state = "silence"
        self.consecutive_count = 0

    def process_audio_block(self, indata):
        # Access the desired channel
        selected_channel_data = indata[:, self.target_channel]

        # Convert audio data to pitch
        pitch = self.pitch_detector(selected_channel_data.astype(np.float32))[0]

        if self.min_freq < pitch < self.max_freq:
            note, octave, cents_difference = frequency_to_note(pitch)
            current_state = f"{note},{octave}"

            if current_state == self.previous_state:
                self.consecutive_count += 1
            else:
                self.consecutive_count = 1
                self.previous_state = current_state

            # Trigger event if the same note is detected consecutively
            if self.consecutive_count == 5:
                self.on_note_detected(note, octave, pitch, cents_difference)
        else:
            # Silence detected
            self.previous_state = "silence"
            self.consecutive_count = 0

    def on_note_detected(self, note, octave, pitch, cents_difference):
        """Callback when a note is detected. Override for custom actions."""
        print(f"Detected note: {note_index_to_text(note)}{octave} ({pitch:.2f} Hz) ({cents_difference} cents)")
