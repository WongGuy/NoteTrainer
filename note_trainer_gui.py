# note_trainer_gui.py

import tkinter as tk
from tkinter import ttk, messagebox  # Imported messagebox for pop-up messages
from config import *

class NoteTrainerGUI:
    def __init__(self, root, target_note, note_queue, stats_tracker):
        self.root = root
        self.root.geometry("1080x960")
        self.stats_tracker = stats_tracker  # Store stats_tracker

        self.target_note_var = tk.StringVar(value=target_note)
        self.detected_note_var = tk.StringVar(value="None")
        self.queue_vars = [tk.StringVar(value=note) for note in note_queue]
        self.correct_note_count_var = tk.StringVar(value="0")
        self.incorrect_note_count_var = tk.StringVar(value="0")
        self.note_accuracy_var = tk.StringVar(value="0%")
        self.average_time_var = tk.StringVar(value="0.0")

        self.note_info_array = [tk.StringVar(value=f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}\n(0)") for idx in range(17)]
        self.note_time_avg_array = [tk.StringVar(value="0.00") for _ in range(17)]

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
                     font=('Helvetica', 18),
                     anchor='center')
        
        self.style.configure('BlackKey.TLabel',
                     foreground='white',
                     background='black',
                     font=('Helvetica', 18),
                     anchor='center')

        # Set up equal row distribution
        for i in range(12):
            frame.grid_rowconfigure(i, weight=1)  # 12 evenly distributed rows

        for j in range(12):
            frame.grid_columnconfigure(j, weight=1)

        # Create All Elements
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
            style_name = 'WhiteKey.TLabel'
            if idx in black_keys:
                style_name = 'BlackKey.TLabel'

            note_info_text.append(ttk.Label(frame, textvariable=self.note_info_array[idx], style=style_name))
            note_time_avg_label.append(ttk.Label(frame, textvariable=self.note_time_avg_array[idx], style=style_name))

        target_note_text = ttk.Label(frame, text="Target Note", font=('Helvetica', 24))
        target_note_label = ttk.Label(frame, textvariable=self.target_note_var, font=('Helvetica', 60, 'bold'))

        # Create the buttons
        reset_button = ttk.Button(frame, text="Reset Stats", command=self.reset_stats)
        copy_button = ttk.Button(frame, text="Copy Full Stats", command=self.copy_stats_to_clipboard)
        quick_copy_button = ttk.Button(frame, text="Copy Quick Stats", command=self.copy_quick_stats_to_clipboard)

        # Layout Time
        detected_note_text.grid(column=0, row=0, columnspan=3, padx=5, pady=0)
        detected_note_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)

        correct_note_text.grid(column=3, row=0, columnspan=2, padx=5, pady=0)
        correct_note_label.grid(column=3, row=1, columnspan=2, padx=5, pady=5)

        incorrect_note_text.grid(column=5, row=0, columnspan=2, padx=5, pady=0)
        incorrect_note_label.grid(column=5, row=1, columnspan=2, padx=5, pady=5)

        note_accuracy_text.grid(column=7, row=0, columnspan=2, padx=5, pady=0)
        note_accuracy_label.grid(column=7, row=1, columnspan=2, padx=5, pady=5)

        average_time_text.grid(column=9, row=0, columnspan=2, padx=5, pady=0)
        average_time_label.grid(column=9, row=1, columnspan=2, padx=5, pady=5)

        ttk.Label(frame, text="Avg. Note Time", font=('Helvetica', 24)).grid(column=0, row=2, columnspan=12, padx=5, pady=5)

        index = 0  # Initialize the index for the note_info_text and note_time_avg_label lists

        black_keys = [1, 3, 6, 8, 10]
        for column in range(12):
            if column in black_keys:
                # Place the first set of items in the column
                note_info_text[index].grid(column=column, row=3, rowspan=1, padx=0, pady=0, sticky='nsew')
                note_time_avg_label[index].grid(column=column, row=4, rowspan=1, padx=0, pady=0, sticky='nsew')
                index += 1  # Move to the next index

                # Place the second set of items in the column
                note_info_text[index].grid(column=column, row=5, rowspan=1, padx=0, pady=0, sticky='nsew')
                note_time_avg_label[index].grid(column=column, row=6, rowspan=1, padx=0, pady=0, sticky='nsew')
                index += 1  # Move to the next index
            else:
                # Place a single set of items in the column
                note_info_text[index].grid(column=column, row=3, rowspan=2, padx=0, pady=0, sticky='nsew')
                note_time_avg_label[index].grid(column=column, row=5, rowspan=2, padx=0, pady=0, sticky='nsew')
                index += 1  # Move to the next index

        ttk.Label(frame, text="Notes", font=('Helvetica', 24)).grid(column=0, row=7, columnspan=12, padx=5, pady=5)

        target_note_text.grid(column=0, row=8, columnspan=2, padx=0, pady=5)
        target_note_label.grid(column=0, row=9, columnspan=2, padx=0, pady=5)

        # Fill out the queue
        for idx, var in enumerate(self.queue_vars):
            label = ttk.Label(frame, textvariable=var, font=('Helvetica', 60))
            label.grid(column=2 + 2 * idx, row=9, columnspan=2, padx=0, pady=5)

        # Place the buttons on the grid on row 10
        reset_button.grid(column=3, row=10, columnspan=2, padx=5, pady=5)
        copy_button.grid(column=5, row=10, columnspan=2, padx=5, pady=5)
        quick_copy_button.grid(column=7, row=10, columnspan=2, padx=5, pady=5)

    def update_detected_note(self, note):
        self.detected_note_var.set(note)

    def update_target_note_and_queue(self, new_target_note, note_queue):
        self.target_note_var.set(new_target_note)
        for idx, var in enumerate(self.queue_vars):
            if idx < len(note_queue):
                var.set(note_queue[idx])
            else:
                var.set('')

    def update_stats(self, stats_tracker):
        # Update correct and incorrect note counts
        self.correct_note_count_var.set(str(stats_tracker.correct_note_count))
        self.incorrect_note_count_var.set(str(stats_tracker.incorrect_note_count))
        accuracy = 100.0*stats_tracker.correct_note_count/(stats_tracker.correct_note_count + stats_tracker.incorrect_note_count)
        self.note_accuracy_var.set(f"{accuracy:.0f}%")
        # Update average time between notes
        average_time = stats_tracker.get_average_time_between_notes()
        self.average_time_var.set(f"{average_time:.2f}")
        # Update average time for each individual note
        for idx, note in enumerate(NOTE_NAMES_SHARP_AND_FLAT):
            avg_time = stats_tracker.get_average_time_for_note(note)
            note_plays = stats_tracker.get_note_plays(note)
            self.note_time_avg_array[idx].set(f"{avg_time:.2f}")
            self.note_info_array[idx].set(f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}\n({note_plays})")

    # Method to reset statistics
    def reset_stats(self):
        self.stats_tracker.reset()
        # Reset GUI variables
        self.correct_note_count_var.set("0")
        self.incorrect_note_count_var.set("0")
        self.note_accuracy_var.set("0%")
        self.average_time_var.set("0.00")
        for idx in range(17):
            self.note_info_array[idx].set(f"{NOTE_NAMES_SHARP_AND_FLAT[idx]}(0)")
            self.note_time_avg_array[idx].set("0.00")
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

