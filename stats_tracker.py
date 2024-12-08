# stats_tracker.py

import time
from collections import defaultdict
from config import *

class StatsTracker:
    def __init__(self):
        self.correct_note_count = 0
        self.incorrect_note_count = 0
        self.last_correct_note_time = None
        self.total_time_between_notes = 0
        self.note_intervals_count = 0
        self.note_times = defaultdict(lambda: {'total_time': 0, 'count': 0})
    
    def increment_correct_notes(self, note):
        current_time = time.time()
        if self.last_correct_note_time is not None:
            interval = current_time - self.last_correct_note_time
            if interval < PAUSE_TIME_SECONDS:
                self.total_time_between_notes += interval
                self.note_intervals_count += 1
                self.note_times[note]['total_time'] += interval
                self.note_times[note]['count'] += 1
        
        self.correct_note_count += 1
        self.last_correct_note_time = current_time
        
    def increment_incorrect_notes(self):
        self.incorrect_note_count += 1

    # New method to reset statistics
    def reset(self):
        self.correct_note_count = 0
        self.incorrect_note_count = 0
        self.last_correct_note_time = None
        self.total_time_between_notes = 0
        self.note_intervals_count = 0
        self.note_times.clear()
    
    # New method to format stats for clipboard
    def get_stats_for_clipboard(self):
        output = []
        output.append("Note\tAvg Time")
        for note in NOTE_NAMES_SHARP_AND_FLAT:
            # plays = self.get_note_plays(note)
            avg_time = self.get_average_time_for_note_string(note)
            output.append(f"{note}\t{avg_time}")
        output.append(f"Total Correct Notes:\t{self.correct_note_count}")
        output.append(f"Total Incorrect Notes:\t{self.incorrect_note_count}")
        total_attempts = self.correct_note_count + self.incorrect_note_count
        accuracy = self.get_accuracy_string()
        output.append(f"Accuracy:\t{accuracy}%")
        avg_time_between_notes = self.get_average_time_between_notes_string()
        output.append(f"Average Time Between Notes:\t{avg_time_between_notes}")
        return "\n".join(output)
    
    def get_quick_stats_for_clipboard(self):
        output = []
        for note in NOTE_NAMES_SHARP_AND_FLAT:
            avg_time = self.get_average_time_for_note_string(note)
            output.append(f"{avg_time}")
        output.append(f"{self.correct_note_count}")
        output.append(f"{self.incorrect_note_count}")
        total_attempts = self.correct_note_count + self.incorrect_note_count
        accuracy = self.get_accuracy_string()
        output.append(f"{accuracy}%")
        avg_time_between_notes = self.get_average_time_between_notes_string()
        output.append(f"{avg_time_between_notes}")
        return "\n".join(output)

    def get_accuracy_string(self):
        if self.correct_note_count + self.incorrect_note_count == 0:
            return '-'
        return f"{(100.0*self.correct_note_count/(self.correct_note_count + self.incorrect_note_count)):.0f}"

    def get_average_time_between_notes_string(self):
        if self.note_intervals_count == 0:
            return "-"
        return f"{(self.total_time_between_notes / self.note_intervals_count):.2f}"
    
    def get_average_time_for_note_string(self, note):
        data = self.note_times[note]
        if data['count'] < 1:
            return '-'
        return f"{(data['total_time'] / data['count']):.2f}"
    
    def get_note_plays(self, note):
        data = self.note_times[note]
        return int(data['count'])
