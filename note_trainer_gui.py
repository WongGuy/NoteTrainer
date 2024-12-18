# note_trainer_gui.py

import tkinter as tk
from tkinter import ttk, messagebox  
from config import *
from functools import partial
from note_utils import text_is_sharp, text_is_flat, text_is_natural 
from note_queue import NoteQueue
from note_detector import NoteDetector

class NoteTrainerGUI:
    def __init__(self, root, stats_tracker, note_queue, note_detector):
        
        self.root = root
        self.root.geometry("1080x960")
        self.stats_tracker = stats_tracker 
        self.note_queue = note_queue
        self.note_detector = note_detector

        self.notes_queue_vars = self.note_queue.get_notes_queue()
        self.target_roots_queue_vars = [tk.StringVar(value=notes['root']) for notes in self.notes_queue_vars]
        self.target_tones_queue_vars = [[tk.StringVar(value="") for _ in range(4)] for _ in range(4)]
        for note_idx, notes in enumerate(self.notes_queue_vars):
            for tone_idx, tone in enumerate(notes['tones']):
                self.target_tones_queue_vars[note_idx][tone_idx].set(tone)

        self.detected_note_var = tk.StringVar(value="None")
        self.note_enabled_var = [tk.BooleanVar(value=True) for note in NOTE_NAMES_SHARP_AND_FLAT]
        self.tone_enabled_var = [tk.BooleanVar(value=False) for tone in INTERVALS]
        self.tone_enabled_var[0].set(True)
        self.correct_note_count_var = tk.StringVar(value="0")
        self.incorrect_note_count_var = tk.StringVar(value="0")
        self.note_accuracy_var = tk.StringVar(value="-%")
        self.average_time_var = tk.StringVar(value="-")

        self.note_info_array = []
        black_keys = [1, 2, 4, 5, 8, 9, 11, 12, 14, 15]
        for idx, _ in enumerate(NOTE_NAMES_SHARP_AND_FLAT):
            if idx in black_keys:
                self.note_info_array.append(tk.StringVar(value=f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}\n(0)"))
            else:
                self.note_info_array.append(tk.StringVar(value=f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}\n(0)"))
        self.note_time_avg_array = [tk.StringVar(value="-") for _ in NOTE_NAMES_SHARP_AND_FLAT]

        self._setup_gui()

    def _setup_gui(self):
        # Create a style object
        self.style = ttk.Style()
        self.style.theme_use('clam')

        frame = ttk.Frame(self.root, style='TFrame')
        frame.pack(fill='both', expand=True)
        
        self.style.configure('WhiteKey.TLabel',
                     foreground='black',
                     background='white',
                     font=('Courier New', 18, 'bold'),
                     anchor='center')
        
        self.style.configure('BlackKey.TLabel',
                     foreground='white',
                     background='black',
                     font=('Courier New', 18, 'bold'),
                     anchor='center')

        # Set up equal row distribution
        for row in range(24):
            frame.grid_rowconfigure(row, weight=1)

        for column in range(24):
            frame.grid_columnconfigure(column, weight=1)

        # Create All Elements
        root_checkboxes = []
        tone_checkboxes = []
        for idx, note_name in enumerate(NOTE_NAMES_SHARP_AND_FLAT):
            root_checkboxes.append(ttk.Checkbutton(
                frame, 
                text=f"{note_name}", 
                variable=self.note_enabled_var[idx], 
                command=partial(self.update_enabled_note, note_name, idx)))
        for idx, tone_name in enumerate(INTERVALS):
            tone_checkboxes.append(ttk.Checkbutton(
                frame, 
                text=f"{tone_name}", 
                variable=self.tone_enabled_var[idx], 
                command=partial(self.update_enabled_tone, tone_name, idx)))

        detected_note_text = ttk.Label(frame, text="Detected", font=('Helvetica', 24))
        detected_note_label = ttk.Label(frame, textvariable=self.detected_note_var, font=('Helvetica', 36))

        correct_note_text = ttk.Label(frame, text="Correct", font=('Helvetica', 24))
        correct_note_label = ttk.Label(frame, textvariable=self.correct_note_count_var, font=('Helvetica', 36))

        incorrect_note_text = ttk.Label(frame, text="Incorrect", font=('Helvetica', 24))
        incorrect_note_label = ttk.Label(frame, textvariable=self.incorrect_note_count_var, font=('Helvetica', 36))

        note_accuracy_text = ttk.Label(frame, text="Accuracy", font=('Helvetica', 24))
        note_accuracy_label = ttk.Label(frame, textvariable=self.note_accuracy_var, font=('Helvetica', 36))

        average_time_text = ttk.Label(frame, text="Avg Time", font=('Helvetica', 24))
        average_time_label = ttk.Label(frame, textvariable=self.average_time_var, font=('Helvetica', 36))

        # Create labels for individual note average times
        note_info_text = []
        note_time_avg_label = []
        black_keys = [1, 2, 4, 5, 8, 9, 11, 12, 14, 15]
        for idx in range(17):
            if idx in black_keys:
                style_name = 'BlackKey.TLabel'
            else:
                style_name = 'WhiteKey.TLabel'

            note_info_text.append(ttk.Label(frame, textvariable=self.note_info_array[idx], style=style_name))
            note_time_avg_label.append(ttk.Label(frame, textvariable=self.note_time_avg_array[idx], style=style_name))

        target_note_text = ttk.Label(frame, text="Target Note", font=('Helvetica', 12))

        # Create the buttons
        regen_queue_button = ttk.Button(frame, text="Reset Queue", command=self.reset_queue)
        reset_stats_button = ttk.Button(frame, text="Reset Stats", command=self.reset_stats)
        copy_button = ttk.Button(frame, text="Copy Full Stats", command=self.copy_stats_to_clipboard)
        quick_copy_button = ttk.Button(frame, text="Copy Quick Stats", command=self.copy_quick_stats_to_clipboard)

        # Layout Time
        ttk.Label(frame, text="Notes To Generate", font=('Helvetica', 18)).grid(column=0, row=0, columnspan=12, padx=5, pady=5)
        ttk.Label(frame, text="Chord Tones to Target", font=('Helvetica', 18)).grid(column=12, row=0, columnspan=12, padx=5, pady=5)
        checkbox_row = 0
        for idx, note in enumerate(NOTE_NAMES_SHARP_AND_FLAT):
            if text_is_natural(note):
                root_checkboxes[idx].grid(column=4*(checkbox_row//4), row=1+checkbox_row%4, columnspan = 2, padx=10, pady=0, sticky='w')
                checkbox_row += 1
            elif text_is_sharp(note):
                root_checkboxes[idx].grid(column=4*(checkbox_row//4), row=1+checkbox_row%4, columnspan = 2, padx=10, pady=0, sticky='w')
            else:
                root_checkboxes[idx].grid(column=4*(checkbox_row//4) + 2, row=1+checkbox_row%4, columnspan = 2, padx=0, pady=0, sticky='w')
                checkbox_row += 1
        
        for idx, _ in enumerate(INTERVALS):
            tone_checkboxes[idx].grid(column=12 + 2*(idx//4), row=1+idx%4, columnspan = 2, padx=0, pady=0, sticky='ew')

        detected_note_text.grid(column=0, row=5, columnspan=6, padx=5, pady=0)
        detected_note_label.grid(column=0, row=6, columnspan=6, padx=5, pady=5)

        correct_note_text.grid(column=6, row=5, columnspan=4, padx=5, pady=0)
        correct_note_label.grid(column=6, row=6, columnspan=4, padx=5, pady=5)

        incorrect_note_text.grid(column=10, row=5, columnspan=4, padx=5, pady=0)
        incorrect_note_label.grid(column=10, row=6, columnspan=4, padx=5, pady=5)

        note_accuracy_text.grid(column=14, row=5, columnspan=4, padx=5, pady=0)
        note_accuracy_label.grid(column=14, row=6, columnspan=4, padx=5, pady=5)

        average_time_text.grid(column=18, row=5, columnspan=4, padx=5, pady=0)
        average_time_label.grid(column=18, row=6, columnspan=4, padx=5, pady=5)

        ttk.Label(frame, text="Avg. Note Time", font=('Helvetica', 24)).grid(column=0, row=7, columnspan=24, padx=5, pady=5)

        index = 0  # Initialize the index for the note_info_text and note_time_avg_label lists

        black_keys = [1, 3, 6, 8, 10]
        for column in range(12):
            if column in black_keys:
                # Place the first set of items in the column
                note_info_text[index].grid(column=2*column, columnspan=2, row=8, rowspan=1, padx=0, pady=0, sticky='nsew')
                note_time_avg_label[index].grid(column=2*column, columnspan=2, row=9, rowspan=1, padx=0, pady=0, sticky='nsew')
                index += 1  # Move to the next index

                # Place the second set of items in the column
                note_info_text[index].grid(column=2*column, columnspan=2, row=10, rowspan=1, padx=0, pady=0, sticky='nsew')
                note_time_avg_label[index].grid(column=2*column, columnspan=2, row=11, rowspan=1, padx=0, pady=0, sticky='nsew')
                index += 1  # Move to the next index
            else:
                # Place a single set of items in the column
                note_info_text[index].grid(column=2*column, columnspan=2, row=8, rowspan=2, padx=0, pady=0, sticky='nsew')
                note_time_avg_label[index].grid(column=2*column, columnspan=2, row=10, rowspan=2, padx=0, pady=0, sticky='nsew')
                index += 1  # Move to the next index

        ttk.Label(frame, text="Notes", font=('Helvetica', 24)).grid(column=0, row=12, columnspan=24, padx=5, pady=5)

        target_note_text.grid(column=0, row=13, columnspan=4, padx=0, pady=5)

        # Fill out the roots queue
        for idx, var in enumerate(self.target_roots_queue_vars):
            label = ttk.Label(frame, textvariable=var, font=('Helvetica', 72, 'bold'), anchor="center")
            label.grid(column=idx*6, row=14, columnspan=6, padx=0, pady=5)
        
        for root_idx, root_var in enumerate(self.target_tones_queue_vars):
            for tone_idx, tone_var in enumerate(root_var):
                label = ttk.Label(frame, textvariable=tone_var, font=('Helvetica', 18, 'bold'), anchor="center")
                label.grid(column=root_idx*6 + tone_idx + 1, row=15, columnspan=1, padx=0, pady=5)

        # Place the buttons on the grid on row 10
        regen_queue_button.grid(column=4, row=16, columnspan=4, padx=5, pady=5, sticky='ew')
        reset_stats_button.grid(column=8, row=16, columnspan=4, padx=5, pady=5, sticky='ew')
        copy_button.grid(column=12, row=16, columnspan=4, padx=5, pady=5, sticky='ew')
        quick_copy_button.grid(column=16, row=16, columnspan=4, padx=5, pady=5, sticky='ew')

    def update_enabled_note(self, note, idx):
        num_checked = sum(var.get() for var in self.note_enabled_var)
        if num_checked < 5:
            self.note_enabled_var[idx].set(1)
            messagebox.showinfo("Minimum Selection", "At least 5 notes must be selected.")
        else:
            enabled = self.note_enabled_var[idx].get()
            self.note_queue.set_root_enabled(note, enabled)

    def update_enabled_tone(self, tone, idx):
        num_checked = sum(var.get() for var in self.tone_enabled_var)
        if num_checked < 1:
            self.tone_enabled_var[idx].set(1)
            messagebox.showinfo("Minimum Selection", "At least 1 interval must be selected.")
        else:
            enabled = self.tone_enabled_var[idx].get()
            self.note_queue.set_tone_enabled(tone, enabled)


    def update_detected_note(self, note):
        self.detected_note_var.set(note)

    def update_target_note_and_queue(self, notes_queue):
        for idx, var in enumerate(self.target_roots_queue_vars):
            var.set(notes_queue[idx]['root'])
        for note_idx, notes_var in enumerate(self.target_tones_queue_vars):
            for tone_idx, tone_var in enumerate(notes_var):
                if tone_idx < len(notes_queue[note_idx]['tones']):
                    tone_var.set(notes_queue[note_idx]['tones'][tone_idx])
                else:
                    tone_var.set('')


    def update_stats(self, stats_tracker):
        # Update correct and incorrect note counts
        self.correct_note_count_var.set(str(stats_tracker.correct_note_count))
        self.incorrect_note_count_var.set(str(stats_tracker.incorrect_note_count))
        accuracy = stats_tracker.get_accuracy_string()
        self.note_accuracy_var.set(f"{accuracy}%")
        # Update average time between notes
        average_time = stats_tracker.get_average_time_between_notes_string()
        self.average_time_var.set(f"{average_time}")
        # Update average time for each individual note
        for idx, note in enumerate(NOTE_NAMES_SHARP_AND_FLAT):
            avg_time = stats_tracker.get_average_time_for_note_string(note)
            note_plays = stats_tracker.get_note_plays(note)
            self.note_time_avg_array[idx].set(f"{avg_time}")
            self.note_info_array[idx].set(f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}\n({note_plays})")

    def reset_queue(self):
        self.note_queue.reset_queue()
        self.update_target_note_and_queue(self.note_queue.get_notes_queue())
        

    # Method to reset statistics
    def reset_stats(self):
        self.stats_tracker.reset()
        # Reset GUI variables
        self.correct_note_count_var.set("0")
        self.incorrect_note_count_var.set("0")
        self.note_accuracy_var.set("-%")
        self.average_time_var.set("-")
        for idx in range(17):
            self.note_info_array[idx].set(f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}\n(0)")
            self.note_time_avg_array[idx].set("-")
        self.detected_note_var.set("None")
        # messagebox.showinfo("Reset Stats", "Statistics have been reset.")

    # Method to copy statistics to clipboard
    def copy_stats_to_clipboard(self):
        # Collect stats from stats_tracker
        stats = self.stats_tracker.get_stats_for_clipboard()
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(stats)
        self.root.update()  # Keeps the clipboard content after the program exits
        # messagebox.showinfo("Copy Stats", "Statistics have been copied to the clipboard.")

    # Method to copy statistics to clipboard
    def copy_quick_stats_to_clipboard(self):
        # Collect stats from stats_tracker
        stats = self.stats_tracker.get_quick_stats_for_clipboard()
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(stats)
        self.root.update()  # Keeps the clipboard content after the program exits
        # messagebox.showinfo("Copy Stats", "Statistics have been copied to the clipboard.")

