#!/usr/bin/env python3

import argparse
import wave

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prüft eine ICS-43434 WAV-Aufnahme."
    )
    parser.add_argument(
        "filename",
        help="WAV-Datei, z. B. test.wav",
    )
    args = parser.parse_args()

    with wave.open(args.filename, "rb") as w:
        channels = w.getnchannels()
        sample_rate = w.getframerate()
        sample_width = w.getsampwidth()
        frames = w.getnframes()
        data = w.readframes(frames)

    print()
    print("============================")
    print("ICS-43434 AUDIO TEST")
    print("============================")
    print("Kanäle:", channels)
    print("Sample Rate:", sample_rate)
    print("Bytes pro Sample:", sample_width)
    print("Samples:", frames)

    audio = np.frombuffer(data, dtype=np.int32)

    if audio.size == 0:
        print("Keine Samples gefunden.")
        return 1

    print()
    print("Minimum:", audio.min())
    print("Maximum:", audio.max())

    rms = np.sqrt(
        np.mean(
            audio.astype(np.float64) ** 2
        )
    )

    print("RMS:", rms)
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
