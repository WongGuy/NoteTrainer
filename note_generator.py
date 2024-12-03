# note_generator.py

import random
from note_utils import text_to_note_index
from config import NOTE_NAMES_SHARP_AND_FLAT

class NoteGenerator:
    def __init__(self):
        # Initialize all notes as enabled by default
        self.enabled_roots = {note: True for note in NOTE_NAMES_SHARP_AND_FLAT}

    def get_valid_notes(self, last_note):
        # Build the valid notes list based on the constraints
        valid_notes = []

        # Filter notes based on sharps_enabled and flats_enabled
        for note in self.enabled_roots:
            if not self.enabled_roots[note]:
                continue  # Skip disabled notes
            if text_to_note_index(note) != text_to_note_index(last_note): # Skip immediate repeats
                valid_notes.append(note)

        return valid_notes

    def get_note(self, last_note):
        valid_notes = self.get_valid_notes(last_note)
        if not valid_notes:
            raise ValueError("No valid notes available to generate.")
        return random.choice(valid_notes)

    def get_note_queue(self, queue_size, last_note):
        note_queue = []
        current_last_note = last_note

        for _ in range(queue_size):
            new_note = self.get_note(current_last_note)
            note_queue.append(new_note)
            current_last_note = new_note  # Update the last note

        return note_queue

    def set_note_enabled(self, note, enabled):
        if note in self.enabled_roots:
            self.enabled_roots[note] = enabled
        else:
            raise ValueError(f"Note '{note}' is not recognized.")

    def get_enabled_roots(self):
        return [note for note, enabled in self.enabled_roots.items() if enabled]
