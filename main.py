# main.py

import os
from queue import Queue, Empty
import tkinter as tk
from tkinter import messagebox
from config import *
from audio_device import get_device_info
from note_utils import text_to_note_index
from custom_note_detector import GUINoteDetector
from note_trainer_gui import NoteTrainerGUI
from audio_handler import AudioHandler
from stats_tracker import StatsTracker
from device_config import DeviceConfig
from note_queue import NoteQueue

def main():
    try: 
        # Create a temporary root window for the device selection dialog
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the temporary root window

        # Device selection dialog
        device_config = DeviceConfig(temp_root, title="Select Input Device")
        temp_root.destroy()  # Destroy the temporary root window after the dialog is done
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received during device setup. Exiting...")

    if device_config.device_id is None or device_config.total_input_channels is None:
        messagebox.showerror("Error", "Device selection failed or was canceled. Exiting.")
        return

    # Get device info
    device_info = get_device_info(device_config.device_id)

    # Initialize Tkinter window
    root = tk.Tk()
    root.title("Note Trainer")

    stats_tracker = StatsTracker()
    note_queue = NoteQueue(QUEUE_SIZE, stats_tracker)
    gui_queue = Queue()

    note_detector = GUINoteDetector(
        buffer_size=BUFFER_SIZE,
        hop_size=HOP_SIZE,
        samplerate=SAMPLERATE,
        silence_threshold=device_config.silence,
        min_freq=MIN_FREQUENCY,
        max_freq=MAX_FREQUENCY,
        target_channel=device_config.target_channel,
        A4=device_config.A4,
        gui_queue=gui_queue 
    )

    # Initialize GUI
    gui = NoteTrainerGUI(root, stats_tracker, note_queue, note_detector)

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
                    if text_to_note_index(detected_note) == note_queue.get_target_note_idx():
                        # Update the note queue
                        note_queue.process_correct_note_detected()
                        # Update the GUI
                        gui.update_target_note_and_queue(note_queue.get_notes_queue())
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
