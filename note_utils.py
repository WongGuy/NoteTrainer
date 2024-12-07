# note_utils.py

import numpy as np
from config import *

def frequency_to_note(freq):
    if freq <= 0:
        return "Silence"
    
    # Calculate MIDI note number
    midi_note = 69 + 12 * np.log2(freq / A4)
    rounded_midi_note = int(np.round(midi_note))

    octave = rounded_midi_note // 12 - 1
    note = rounded_midi_note % 12

    
    # Calculate cents difference
    rounded_freq = A4 * 2 ** ((rounded_midi_note - 69) / 12)
    cents_difference = int(1200 * np.log2(freq / rounded_freq))
    
    return note, octave, cents_difference

def note_index_to_text(note):
    return NOTE_NAMES_ALL[note]

def text_to_note_index(note):
    if note in NOTE_NAMES_ALL:
        note = NOTE_NAMES_ALL.index(note)
    elif note in NOTE_NAMES_SHARP:
        note = NOTE_NAMES_SHARP.index(note)
    elif note in NOTE_NAMES_FLAT:
        note = NOTE_NAMES_FLAT.index(note)
    else: 
        note = -1

    return note

def text_is_sharp(note):
    return note in NOTE_NAMES_SHARP_ONLY

def text_is_flat(note):
    return note in NOTE_NAMES_FLAT_ONLY

def text_is_natural(note):
    return note in NOTE_NAMES_NATURAL_ONLY