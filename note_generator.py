import random
from note_utils import *
from config import *

def get_note(last_note, sharps_enabled, flats_enabled):
    # Determine the index of the last note in both lists
    last_note_index = text_to_note(last_note)
    # Build the valid notes list based on the constraints
    valid_notes = []
    
    if sharps_enabled:
        valid_notes.extend([note for i, note in enumerate(NOTE_NAMES_SHARP) if i != last_note_index])
    if flats_enabled:
        valid_notes.extend([note for i, note in enumerate(NOTE_NAMES_FLAT) if i != last_note_index])
    if not sharps_enabled and not flats_enabled:
        # Only natural notes are allowed
        valid_notes.extend([NOTE_NAMES_SHARP[i] for i in range(12) if '#' not in NOTE_NAMES_SHARP[i] and 'b' not in NOTE_NAMES_SHARP[i] and i != last_note_index])
    
    # Remove duplicates in case sharps and flats are both enabled
    valid_notes = list(set(valid_notes))
    
    # Randomly select a note from the valid list
    return random.choice(valid_notes)

def get_note_queue(queue_size, last_note, sharps_enabled, flats_enabled):
    # Generate a queue of notes based on the constraints
    note_queue = []
    current_last_note = last_note
    
    for _ in range(queue_size):
        new_note = get_note(current_last_note, sharps_enabled, flats_enabled)
        note_queue.append(new_note)
        current_last_note = new_note  # Update the last note
    
    return note_queue
