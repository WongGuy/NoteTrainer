import os
# Set environment variable for ASIO, MUST GO BEFORE IMPORTING SOUNDDEVICE
os.environ["SD_ENABLE_ASIO"] = "1"

import sounddevice as sd

class AudioHandler:
    def __init__(self, device_id, samplerate, blocksize, channels, callback):
        self.stream = sd.InputStream(
            device=device_id,
            callback=callback,
            samplerate=samplerate,
            blocksize=blocksize,
            channels=channels
        )

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()
