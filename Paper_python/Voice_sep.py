# input x(signal), N(Number of samples in each Hamming window for STFT)
#output 
import numpy as np;
import scipy


x = np.zeros(10)
N = 100




f, t, X = scipy.stft(x, window='hamming', nperseg=N, noverlap=N//2, return_onesided=True) # get stft of x

V = np.abs(X) #magnitude spectrogram V



import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from numpy.fft import fft, ifft

FRAME_SIZE = 2048

################## YOUR CODE HERE ######################
def ece420ProcessFrame(frame, Fs):
    freq = -1
    Es = 0
    for i in range(len(frame)):
        Es += np.absolute(frame[i])  *2 
    Thresh = 200e7
    if(Es > Thresh):
        autoc = np.abs(ifft(np.abs(fft(frame) np.conj(fft(frame)))))
        max = -np.Infinity
        location = 0
        for i in range(50, FRAME_SIZE-50):
            if(autoc[i] > max):
                max = autoc[i]
                location = i

        if(location != 0): freq = Fs/location

    return freq

#def ece420ProcessFrame(frame, Fs):
    freq = -1
    Es = 0
    for i in range(len(frame)):
        Es += np.square(np.absolute(frame[i]))
    Thresh = 1800000000
    if(Es > Thresh):
        autoc = np.abs(ifft(fft(frame)np.conj(fft(frame))))
        max = -np.Infinity
        location = 0
        # need to only check freq between 70Hz - 270Hz for voice detection
        high = int(np.floor(Fs / 70))  # low end of range
        low = int(np.ceil(Fs / 270)) # high end of range
        if(high > FRAME_SIZE - 20):
            high = FRAME_SIZE - 20
        for i in range(low, high):
            if(autoc[i] > max):
                if location != 0: 
                    ratio = i / location
                    if not((ratio > 1.9 and ratio < 2.1) or (ratio > 2.9 and ratio < 3.1)): #check for 2nd and third harmonics
                        max = autoc[i]
                        location = i
                else:
                    max = autoc[i]
                    location = i

        if(location != 0): freq = Fs/location

    return freq