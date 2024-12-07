
from note_detector import NoteDetector
from note_utils import *

class GUINoteDetector(NoteDetector):
    def __init__(self, *args, gui_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.gui_queue = gui_queue
        self.target_note = None  # Will be set in main.py

    def on_note_detected(self, note, octave, pitch, cents_difference):
        detected_note = f"{note_index_to_text(note)}"
        # Send message to GUI via queue
        if self.gui_queue is not None:
            message = {'type': 'NoteDetected', 'note': detected_note}
            self.gui_queue.put(message)
