import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as spwav
import sys
import scipy
import math


from scipy.io.wavfile import read, write
from numpy.fft import fft, ifft
from scipy import signal


def find_closest_fraction(number):
    closest_fraction = None
    min_difference = float('inf')

    for numerator in range(0, 11):
        for denominator in range(1, 11):
            fraction = numerator / denominator
            difference = abs(number - fraction)
            if difference < min_difference:
                min_difference = difference
                closest_fraction = (numerator, denominator)

    return closest_fraction




def get_output(up_,down_,data_i):

    up_ratio = up_
    down_ratio = down_

    output = signal.resample_poly(data_i, up_ratio, down_ratio)
    return output


def generate_sine_wave(frequency, num_samples, sampling_freq):
    t = np.linspace(0, (num_samples-1) / sampling_freq, num_samples)  # Generate time points
    x = np.sin(2 * np.pi * frequency * t)  # Calculate sine values
    return x


def generate_audio(notes, sampling_freq, duration):
    audio = []
    for freq in notes:
        t = np.linspace(0, duration, int(duration * sampling_freq), endpoint=False)
        note = np.sin(2 * np.pi * freq * t)*1000
        audio.extend(note)
    audio = np.array(audio)
    # Scale the audio to be between -1 and 1
    audio /= np.max(np.abs(audio), axis=0)
    return audio