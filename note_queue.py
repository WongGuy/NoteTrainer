# note_queue.py
import random
from note_utils import text_to_note_index
from config import NOTE_NAMES_SHARP_AND_FLAT


class NoteQueue:
    def __init__(self, queue_size):
        self.enabled_roots = {note: True for note in NOTE_NAMES_SHARP_AND_FLAT}
        self.queue_size = queue_size
        # Initialize the target note
        self.target_note = self.get_note('')
        # Initialize the note queue
        self.note_queue = self.initialize_note_queue(self.queue_size, self.target_note)
    
    def get_valid_roots(self, last_note): 
        # Build the valid notes list based on the constraints
        valid_notes = []

        # Filter notes based on sharps_enabled and flats_enabled
        for note in self.enabled_roots:
            if not self.enabled_roots[note]:
                continue  # Skip disabled notes
            if text_to_note_index(note) != text_to_note_index(last_note): # Skip immediate repeats
                valid_notes.append(note)

        return valid_notes

    def get_note(self, last_note): #TODO: This should be get root
        valid_notes = self.get_valid_roots(last_note)
        if not valid_notes:
            raise ValueError("No valid notes available to generate.")
        return random.choice(valid_notes)

    def initialize_note_queue(self, queue_size, last_note): #TODO: This should be get root queue
        note_queue = []
        current_last_note = last_note

        for _ in range(queue_size):
            new_note = self.get_note(current_last_note)
            note_queue.append(new_note)
            current_last_note = new_note  # Update the last note

        return note_queue

    def set_note_enabled(self, note, enabled): #TODO: This should be set root enabled
        if note in self.enabled_roots:
            self.enabled_roots[note] = enabled
        else:
            raise ValueError(f"Note '{note}' is not recognized.")

    def get_enabled_roots(self):
        return [note for note, enabled in self.enabled_roots.items() if enabled]

    def get_target_note(self):
        return self.target_note
    
    def get_note_queue(self):
        return self.note_queue.copy()
    
    def process_correct_note_detected(self):
        # Move the first note in the note queue to be the new target note
        self.target_note = self.note_queue.pop(0)
        # Add a new random note to the end of the queue
        last_note = self.note_queue[-1] if self.note_queue else self.target_note
        new_note = self.get_note(last_note)
        self.note_queue.append(new_note)
    
    def reset_queue(self):
        self.target_note = self.get_note('')
        self.note_queue = self.initialize_note_queue(self.queue_size, self.target_note)
