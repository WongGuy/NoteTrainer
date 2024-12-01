# main.py

import os
from queue import Queue, Empty
import tkinter as tk
from tkinter import messagebox
from config import *
from audio_device import get_device_info
from note_generator import NoteGenerator
from note_utils import text_to_note_index
from custom_note_detector import GUINoteDetector
from note_trainer_gui import NoteTrainerGUI
from audio_handler import AudioHandler
from stats_tracker import StatsTracker
from device_config import DeviceConfig

def main():
    # Create a temporary root window for the device selection dialog
    temp_root = tk.Tk()
    temp_root.withdraw()  # Hide the temporary root window

    # Device selection dialog
    device_config = DeviceConfig(temp_root, title="Select Input Device")
    temp_root.destroy()  # Destroy the temporary root window after the dialog is done

    if device_config.device_id is None or device_config.total_input_channels is None:
        messagebox.showerror("Error", "Device selection failed or was canceled. Exiting.")
        return

    # Get device info
    device_info = get_device_info(device_config.device_id)
    actual_samplerate = device_info['default_samplerate']
    print(f"Actual device sample rate: {actual_samplerate} Hz")
    print(f"Assumed device sample rate: {SAMPLERATE} Hz")

    # Initialize Tkinter window
    root = tk.Tk()
    root.title("Note Trainer")

    # Initialize NoteGenerator
    note_generator = NoteGenerator()

    # Initialize Target Note and Note Queue
    target_note = note_generator.get_note('')
    note_queue = note_generator.get_note_queue(QUEUE_SIZE, target_note)

    # Initialize StatsTracker
    stats_tracker = StatsTracker()

    # Initialize GUI
    gui = NoteTrainerGUI(root, target_note, note_queue, stats_tracker, note_generator)

    # For thread-safe communication, we'll use a queue
    gui_queue = Queue()

    # Initialize GUINoteDetector
    note_detector = GUINoteDetector(
        buffer_size=BUFFER_SIZE,
        hop_size=HOP_SIZE,
        samplerate=SAMPLERATE,
        silence_threshold=SILENCE,
        min_freq=MIN_FREQUENCY,
        max_freq=MAX_FREQUENCY,
        target_channel=device_config.target_channel,
        gui_queue=gui_queue  # Pass the queue to the note detector
    )
    note_detector.set_target_note(target_note)

    # Define the audio callback function
    def audio_callback(indata, frames, time, status):
        if status:
            print("Status:", status)
        note_detector.process_audio_block(indata)

    # Initialize and start the audio handler
    audio_handler = AudioHandler(
        device_id=device_config.device_id,
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=device_config.total_input_channels,
        callback=audio_callback
    )
    audio_handler.start()
    print(f"Using device ID: {device_config.device_id}, Device Name: {device_info['name']}")

    # Function to periodically check the queue
    def check_queue():
        try:
            while True:
                message = gui_queue.get_nowait()
                if message['type'] == 'NoteDetected':
                    detected_note = message['note']
                    gui.update_detected_note(detected_note)
                    # Check if detected note matches target note
                    if text_to_note_index(detected_note) == text_to_note_index(note_detector.target_note):
                        # Update stats tracker
                        stats_tracker.increment_correct_notes(note_detector.target_note)
                        # Move the first note in the note queue to be the new target note
                        new_target_note = note_queue.pop(0)
                        note_detector.set_target_note(new_target_note)
                        # Add a new random note to the end of the queue
                        new_note = note_generator.get_note(note_queue[-1])
                        note_queue.append(new_note)
                        # Update the queue display variables
                        gui.update_target_note_and_queue(new_target_note, note_queue)
                    else:
                        stats_tracker.increment_incorrect_notes()
                    # Update the GUI with stats from stats_tracker
                    gui.update_stats(stats_tracker)
                gui_queue.task_done()
        except Empty:
            pass
        # Schedule the function to run again after 50 ms
        root.after(50, check_queue)

    # Start checking the queue
    root.after(50, check_queue)

    def on_closing():
        audio_handler.stop()
        root.destroy()

    # Bind the handler to the window's close event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Run the Tkinter main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Stopping the audio stream...")
        root.destroy()
    finally:
        audio_handler.stop()

if __name__ == "__main__":
    main()
