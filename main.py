# main.py

import os
from queue import Queue, Empty
import tkinter as tk
from config import *
from audio_device import find_device_id, get_device_info
from note_generator import get_note, get_note_queue
from note_utils import text_to_note
from custom_note_detector import GUINoteDetector
from note_trainer_gui import NoteTrainerGUI
from audio_handler import AudioHandler
from stats_tracker import StatsTracker

def main():
    # Find device ID
    device_id, device_text_name = find_device_id(DEVICE_NAME)
    if device_id is None:
        print("Device not found. Exiting...")
        raise SystemExit("Device not found. Exiting...")

    # Get device info
    device_info = get_device_info(device_id)
    actual_samplerate = device_info['default_samplerate']
    print(f"Actual device sample rate: {actual_samplerate} Hz")
    print(f"Assumed device sample rate: {SAMPLERATE} Hz")

    # Initialize Tkinter window
    root = tk.Tk()
    root.title("Note Trainer")
    print("Tkinter Window Initialized")

    # Initialize Target Note and Note Queue
    target_note = get_note('C', SHARPS_ENABLED, FLATS_ENABLED)
    note_queue = get_note_queue(QUEUE_SIZE, target_note, SHARPS_ENABLED, FLATS_ENABLED)

    # Initialize StatsTracker
    stats_tracker = StatsTracker()

    # Initialize GUI
    gui = NoteTrainerGUI(root, target_note, note_queue, stats_tracker)

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
        target_channel=TARGET_CHANNEL,
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
        device_id=device_id,
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=TOTAL_INPUT_CHANNELS,
        callback=audio_callback
    )
    audio_handler.start()
    print(f"Using device ID: {device_id}, Device Name: {device_text_name}")

    # Function to periodically check the queue
    def check_queue():
        try:
            while True:
                message = gui_queue.get_nowait()
                if message['type'] == 'NoteDetected':
                    detected_note = message['note']
                    gui.update_detected_note(detected_note)
                    # Check if detected note matches target note
                    if text_to_note(detected_note) == text_to_note(note_detector.target_note):
                        # Update stats tracker
                        stats_tracker.increment_correct_notes(note_detector.target_note)
                        # Move the first note in the note queue to be the new target note
                        new_target_note = note_queue.pop(0)
                        note_detector.set_target_note(new_target_note)
                        # Add a new random note to the end of the queue
                        new_note = get_note(note_queue[-1], SHARPS_ENABLED, FLATS_ENABLED)
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
