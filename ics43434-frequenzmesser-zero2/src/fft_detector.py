#!/usr/bin/env python3

import numpy as np


def calculate_frequency(
    samples: np.ndarray,
    sample_rate: int,
    min_frequency: float = 20.0,
    max_frequency: float = 8000.0,
):
    """
    Bestimmt die dominante Frequenz eines Audio-Blocks per FFT.

    Rückgabe:
        frequency_hz, magnitude
    """
    if samples.size == 0:
        return 0.0, 0.0

    samples = samples.astype(np.float64, copy=True)

    # DC-Anteil entfernen
    samples -= np.mean(samples)

    # Hanning/Hann-Fenster
    samples *= np.hanning(len(samples))

    # Reelle FFT
    spectrum = np.fft.rfft(samples)
    magnitude = np.abs(spectrum)

    if magnitude.size <= 1:
        return 0.0, 0.0

    # 0 Hz ignorieren
    magnitude[0] = 0.0

    frequencies = np.fft.rfftfreq(len(samples), d=1.0 / sample_rate)

    valid = (
        (frequencies >= min_frequency)
        & (frequencies <= max_frequency)
    )

    if not np.any(valid):
        return 0.0, 0.0

    valid_indices = np.nonzero(valid)[0]
    local_peak = np.argmax(magnitude[valid])
    peak = int(valid_indices[local_peak])

    frequency = float(frequencies[peak])
    peak_magnitude = float(magnitude[peak])

    return frequency, peak_magnitude
