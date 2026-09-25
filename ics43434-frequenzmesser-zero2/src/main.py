#!/usr/bin/env python3

import argparse
import signal

import numpy as np

from audio_capture import AlsaCapture
from fft_detector import calculate_frequency


SAMPLE_RATE = 48000
FFT_SIZE = 4096
CHANNELS = 2

# ICS-43434 mit L/R = GND -> linker Kanal
CHANNEL = 0

MIN_FREQUENCY_HZ = 20.0
MAX_FREQUENCY_HZ = 8000.0


running = True


def stop_program(_signal_number, _frame):
    global running
    running = False


def calculate_rms(samples: np.ndarray) -> float:
    samples = samples.astype(np.float64, copy=False)
    return float(np.sqrt(np.mean(samples * samples)))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Live-Frequenzanalyse für ICS-43434 am Raspberry Pi Zero 2 W"
    )
    parser.add_argument(
        "device",
        help="ALSA-Gerät, z. B. hw:0,0 oder hw:1,0",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=250.0,
        help="RMS-Schwelle für die Anzeige (Standard: 250)",
    )

    args = parser.parse_args()

    print()
    print("======================================")
    print(" ICS-43434 LIVE FFT")
    print(" Raspberry Pi Zero 2 W")
    print("======================================")
    print()
    print("Sample Rate :", SAMPLE_RATE, "Hz")
    print("FFT         :", FFT_SIZE)
    print(
        "Auflösung   :",
        SAMPLE_RATE / FFT_SIZE,
        "Hz",
    )
    print("ALSA-Gerät  :", args.device)
    print("Kanal       :", CHANNEL)
    print()
    print("Mikrofon wird gestartet...")
    print("Beenden mit CTRL+C")
    print()

    capture = AlsaCapture(
        device=args.device,
        channels=CHANNELS,
        sample_rate=SAMPLE_RATE,
    )

    signal.signal(signal.SIGINT, stop_program)

    try:
        capture.start()

        while running:
            data = capture.read_frames(FFT_SIZE)

            # 2 Kanäle × 4 Bytes = 8 Bytes pro Audio-Frame
            raw = np.frombuffer(data, dtype=np.int32)

            if raw.size != FFT_SIZE * CHANNELS:
                print("Unvollständiger FFT-Block.")
                continue

            # Gewünschten Kanal auswählen
            samples = raw[CHANNEL::CHANNELS].astype(np.float64)

            # RMS als einfacher Pegelindikator
            rms = calculate_rms(samples)

            frequency, magnitude = calculate_frequency(
                samples,
                sample_rate=SAMPLE_RATE,
                min_frequency=MIN_FREQUENCY_HZ,
                max_frequency=MAX_FREQUENCY_HZ,
            )

            if rms < args.threshold:
                print(
                    f"Frequenz:      --- Hz | "
                    f"RMS: {rms:10.1f} | "
                    f"Peak: {magnitude:12.0f}"
                )
            else:
                print(
                    f"Frequenz: {frequency:8.1f} Hz | "
                    f"RMS: {rms:10.1f} | "
                    f"Peak: {magnitude:12.0f}"
                )

    except RuntimeError as exc:
        print(f"Fehler: {exc}")
        return 1

    finally:
        capture.stop()

    print()
    print("Programm beendet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
