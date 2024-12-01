import os
# Set environment variable for ASIO, MUST GO BEFORE IMPORTING SOUNDDEVICE
os.environ["SD_ENABLE_ASIO"] = "1"

import tkinter as tk
from tkinter import simpledialog, messagebox
import sounddevice as sd


class DeviceConfig(tk.simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.device_id = None
        self.total_input_channels = None
        self.target_channel = None
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Select Input Device:").grid(row=0, column=0, sticky="w")
        self.channel_label = tk.Label(master, text="Target Input Channel:")
        self.channel_label.grid(row=1, column=0, sticky="w")

        # Get list of input devices
        devices = sd.query_devices()
        self.input_devices = [d for d in devices if d['max_input_channels'] > 0]
        # Include device names with their max_input_channels
        self.device_display_names = [
            f"{d['name']} (Channels: {d['max_input_channels']})"
            for d in self.input_devices
        ]

        self.device_var = tk.StringVar()
        self.device_var.set(self.device_display_names[0])  # Default selection

        # Custom dropdown for device selection
        self.device_menu_button = tk.Menubutton(master, textvariable=self.device_var, relief="raised")
        self.device_menu_button.menu = tk.Menu(self.device_menu_button, tearoff=0)
        self.device_menu_button["menu"] = self.device_menu_button.menu

        # Add devices to the menu with bolding for ASIO devices
        for name in self.device_display_names:
            is_asio = "ASIO" in name
            font = "TkDefaultFont" if not is_asio else ("TkDefaultFont", 10, "bold")
            self.device_menu_button.menu.add_radiobutton(
                label=name,
                variable=self.device_var,
                value=name,
                command=lambda n=name: self.update_channel_info(n),
                font=font,
            )

        self.device_menu_button.grid(row=0, column=1, sticky="w")

        self.channel_var = tk.IntVar()
        self.channel_dropdown = tk.OptionMenu(master, self.channel_var, 0)  # Initial default
        self.channel_dropdown.grid(row=1, column=1, sticky="w")

        # Set the initial target input channel label
        self.update_channel_info(self.device_var.get())

        return self.device_menu_button  # initial focus

    def update_channel_info(self, selected_device):
        # Extract device name (before the channel information)
        device_name = selected_device.split(" (Channels:")[0].strip()

        # Find the selected device and update channel label
        for d in self.input_devices:
            if d['name'] == device_name:
                self.total_input_channels = d['max_input_channels']
                self.channel_label.config(
                    text=f"Target Input Channel (0-{self.total_input_channels - 1}):"
                )

                # Update the channel dropdown menu
                menu = self.channel_dropdown['menu']
                menu.delete(0, 'end')
                for i in range(self.total_input_channels):
                    menu.add_command(label=i, command=tk._setit(self.channel_var, i))
                self.channel_var.set(0)  # Reset to default
                break

    def apply(self):
        # Get selected device name from dropdown
        selected_device = self.device_var.get()
        target_channel = self.channel_var.get()

        # Extract device name (before the channel information)
        device_name = selected_device.split(" (Channels:")[0].strip()

        # Find device ID and total input channels
        devices = sd.query_devices()
        for idx, d in enumerate(devices):
            if d['name'] == device_name and d['max_input_channels'] > 0:
                self.device_id = idx
                self.total_input_channels = d['max_input_channels']
                break
        else:
            messagebox.showerror("Error", "Selected device not found.")
            return

        if target_channel < 0 or target_channel >= self.total_input_channels:
            messagebox.showerror("Error", f"Target channel must be between 0 and {self.total_input_channels - 1}.")
            return

        self.target_channel = target_channel
