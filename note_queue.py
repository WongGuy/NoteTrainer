# note_queue.py
import random
from note_utils import text_to_note_index
from config import *


class NoteQueue:
    def __init__(self, queue_size, stats_tracker):
        self.stats_tracker = stats_tracker
        self.enabled_roots = {note: True for note in NOTE_NAMES_SHARP_AND_FLAT}
        self.enabled_tones = {tone: False for tone in INTERVALS.keys()}
        self.enabled_tones['1'] = True
        self.queue_size = queue_size
        
        self.notes_bag = self.generate_notes_bag('')
        self.notes_queue = []
        for i in range(self.queue_size):
            self.notes_queue.append(self.get_notes_from_bag())
    
    def generate_tones(self):
        return self.get_enabled_tones() #TODO: Add more functionality for random tones

    def generate_notes_bag(self, last_root):
        enabled_roots = self.get_enabled_roots()
        if not enabled_roots:
            raise ValueError("No enabled roots available.")
        root_bag = enabled_roots * 2
        total_roots = len(root_bag)

        last_note_index = text_to_note_index(last_root)

        max_shuffle_attempts = 1000
        for attempt in range(max_shuffle_attempts):
            shuffled_bag = root_bag.copy()
            random.shuffle(shuffled_bag)

            # Check if the first note does not match the last_note
            first_root_index = text_to_note_index(shuffled_bag[0])
            if first_root_index == last_note_index:
                continue  # Retry shuffle

            # Check that no two consecutive notes are enharmonically equivalent
            valid = True
            for i in range(1, total_roots):
                prev_index = text_to_note_index(shuffled_bag[i - 1])
                current_index = text_to_note_index(shuffled_bag[i])
                if current_index == prev_index:
                    valid = False
                    break  # Invalid shuffle, retry

            if valid:
                notes_bag = []
                for root in shuffled_bag:
                    notes = {}
                    notes['root'] = root
                    notes['tones'] = self.generate_tones()
                    notes_bag.append(notes)
                
                return notes_bag
        
        # If no valid shuffle is found after max_shuffle_attempts, raise an error
        raise ValueError("Unable to generate a valid note bag with the given constraints.")

    def get_notes_from_bag(self):
        if len(self.notes_bag) == 1:
            last_notes = self.notes_bag.pop(0)
            self.notes_bag = self.generate_notes_bag(last_notes['root'])

            return last_notes
        return self.notes_bag.pop(0)


    def get_valid_notes(self, last_note): 
        valid_notes = []
        for note in self.enabled_roots:
            if not self.enabled_roots[note]:
                continue  # Skip disabled notes
            if text_to_note_index(note) != text_to_note_index(last_note): # Skip immediate repeats
                valid_notes.append(note)

        return valid_notes

    def set_root_enabled(self, note, enabled):
        if note in self.enabled_roots:
            self.enabled_roots[note] = enabled
        else:
            raise ValueError(f"Note '{note}' is not recognized.")

    def get_enabled_roots(self):
        return [note for note, enabled in self.enabled_roots.items() if enabled]
    
    def set_tone_enabled(self, tone, enabled):
        if tone in self.enabled_tones:
            self.enabled_tones[tone] = enabled
        else:
            raise ValueError(f"Note '{tone}' is not recognized.")

    def get_enabled_tones(self):
        return [tone for tone, enabled in self.enabled_tones.items() if enabled]

    def get_target_note_idx(self):
        root_idx = text_to_note_index(self.notes_queue[0]['root'])
        interval = self.notes_queue[0]['tones'][0]
        offset = INTERVALS[interval]
        idx = (root_idx + offset) % 12
        return idx
    
    def get_target_root(self):
        return self.notes_queue[0]['root']
    
    def get_notes_queue(self):
        return self.notes_queue.copy()
    
    def process_correct_note_detected(self):
        self.notes_queue[0]['tones'].pop(0)
        if len(self.notes_queue[0]['tones']) < 1:
            # Update stats tracker
            self.stats_tracker.increment_correct_notes(self.get_target_root())
            self.notes_queue.pop(0)
            new_note = self.get_notes_from_bag()
            self.notes_queue.append(new_note)
        
    
    def reset_queue(self):
        self.notes_bag = self.generate_notes_bag('')
        self.notes_queue = []
        for _ in range(self.queue_size):
            self.notes_queue.append(self.get_notes_from_bag())

