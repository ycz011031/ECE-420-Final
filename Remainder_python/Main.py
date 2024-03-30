import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from numpy.fft import fft, ifft
from Freq_detec import *

FRAME_SIZE = 8192
threshold = (1800000000/2048)*FRAME_SIZE

