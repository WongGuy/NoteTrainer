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
        self.silence = 48
        self.A4 = 440
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

         # Silence Selection
        tk.Label(master, text="Silence (-dB):").grid(row=2, column=0, sticky="w")
        self.silence_var = tk.IntVar()
        self.silence_var.set(48)  # Default silence value

        self.silence_menu_button = tk.Menubutton(master, textvariable=self.silence_var, relief="raised")
        self.silence_menu_button.menu = tk.Menu(self.silence_menu_button, tearoff=0)
        self.silence_menu_button["menu"] = self.silence_menu_button.menu

        silence_options = [6, 12, 18, 24, 30, 36, 42, 48]
        for s in silence_options:
            self.silence_menu_button.menu.add_radiobutton(
                label=str(s),
                variable=self.silence_var,
                value=s
            )

        self.silence_menu_button.grid(row=2, column=1, sticky="w")

        # A4 Selection
        tk.Label(master, text="A4 (Hz):").grid(row=3, column=0, sticky="w")
        self.A4_var = tk.IntVar()
        self.A4_var.set(440)  # Default A4 value

        self.A4_menu_button = tk.Menubutton(master, textvariable=self.A4_var, relief="raised")
        self.A4_menu_button.menu = tk.Menu(self.A4_menu_button, tearoff=0)
        self.A4_menu_button["menu"] = self.A4_menu_button.menu

        A4_options = [432, 434, 436, 438, 440, 442, 444, 446]
        for a in A4_options:
            if a == 440:
                font = ("TkDefaultFont", 10, "bold")
            else:
                font = "TkDefaultFont"
            self.A4_menu_button.menu.add_radiobutton(
                label=str(a),
                variable=self.A4_var,
                value=a,
                font=font
            )

        self.A4_menu_button.grid(row=3, column=1, sticky="w")

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
        selected_silence = self.silence_var.get()
        selected_A4 = self.A4_var.get()

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
        self.silence = selected_silence
        self.A4 = selected_A4
