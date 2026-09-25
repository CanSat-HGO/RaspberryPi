#!/usr/bin/env python3

import subprocess
from typing import Optional


class AlsaCapture:
    """Liest 32-Bit-PCM-Rohdaten über arecord/ALSA."""

    def __init__(
        self,
        device: str,
        channels: int,
        sample_rate: int,
    ):
        self.device = device
        self.channels = channels
        self.sample_rate = sample_rate
        self.process: Optional[subprocess.Popen] = None

    def start(self) -> None:
        command = [
            "arecord",
            "-D",
            self.device,
            "-c",
            str(self.channels),
            "-r",
            str(self.sample_rate),
            "-f",
            "S32_LE",
            "-t",
            "raw",
            "-q",
        ]

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

    def read_frames(self, frames: int) -> bytes:
        if self.process is None or self.process.stdout is None:
            raise RuntimeError("ALSA-Aufnahme wurde noch nicht gestartet.")

        bytes_per_frame = self.channels * 4
        byte_count = frames * bytes_per_frame

        data = self.process.stdout.read(byte_count)

        if len(data) != byte_count:
            raise RuntimeError(
                f"Unvollständige Audiodaten: {len(data)} / {byte_count} Bytes."
            )

        return data

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
