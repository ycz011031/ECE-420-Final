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