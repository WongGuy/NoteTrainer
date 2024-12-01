# device_selection_dialog.py

import tkinter as tk
from tkinter import simpledialog, messagebox
import sounddevice as sd

class DeviceSelectionDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.device_id = None
        self.total_input_channels = None
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Select Input Device:").grid(row=0, column=0, sticky="w")
        tk.Label(master, text="Total Input Channels:").grid(row=1, column=0, sticky="w")

        # Get list of input devices
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        device_names = [d['name'] for d in input_devices]

        self.device_var = tk.StringVar()
        self.device_var.set(device_names[0])  # Default selection

        self.device_menu = tk.OptionMenu(master, self.device_var, *device_names)
        self.device_menu.grid(row=0, column=1, sticky="w")

        self.channels_var = tk.IntVar()
        self.channels_var.set(1)  # Default to 1 channel

        self.channels_entry = tk.Entry(master, textvariable=self.channels_var)
        self.channels_entry.grid(row=1, column=1, sticky="w")

        return self.device_menu  # initial focus

    def apply(self):
        device_name = self.device_var.get()
        total_input_channels = self.channels_var.get()

        # Find device ID
        devices = sd.query_devices()
        for idx, d in enumerate(devices):
            if d['name'] == device_name and d['max_input_channels'] > 0:
                self.device_id = idx
                break
        else:
            messagebox.showerror("Error", "Selected device not found.")
            return

        if total_input_channels <= 0:
            messagebox.showerror("Error", "Total input channels must be positive.")
            return

        self.total_input_channels = total_input_channels
