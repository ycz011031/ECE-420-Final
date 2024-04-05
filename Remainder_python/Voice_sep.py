# input x(signal), N(Number of samples in each Hamming window for STFT)
#output 
import numpy as np;
import scipy
import math


def music_voice_sep(F_s,x,N):

    Music_full = np.zeros(x.shape)

    for channel in range(x.shape[1]):
        current_channel_data = x[:, channel]
        processed_channel_data = TempX(current_channel_data, F_s,N)
        _, Music = scipy.signal.istft(processed_channel_data, fs=F_s, window='hamming', nperseg=N, noverlap=N//2)
        if len(Music) != x.shape[0]:
            Music = np.resize(Music, x.shape[0])
        Music_full[:, channel] = Music
    
    return Music_full




def TempX(x, F_s,N):
    # Constants
    #N = 1024  # Assuming N is defined outside, used for STFT computation
    
    def autoc(frame):
        fft_frame = np.fft.fft(frame)
        power_spectrum = fft_frame * np.conj(fft_frame)
        autoc = np.abs(np.fft.ifft(power_spectrum))
        return autoc
    
    # Perform STFT
    f, t, X = scipy.signal.stft(x, fs=F_s, window='hamming', nperseg=N, noverlap=N//2)
    
    # Compute magnitude spectrogram and square it
    m = len(t)
    n = N / 2 + 1
    V = np.abs(X)
    V_squared = V**2
    B = np.zeros_like(V_squared)
    
    # Autocorrelation row by row
    num_rows = V_squared.shape[0]
    for i in range(num_rows):
        B[i] = autoc(V_squared[i])
    '''

    for i in range (int(n)):
        for j in range (m):
            sum = 0
            for k in range (m - j):
                if k + j - 1 < m:
                    sum = V_squared[i,k]*V_squared[i, k + j]
                else :
                    raise Exception("Autoc out of bounds")
                norm = m - j + 1
                if norm > 0:  # Prevent division by zero
                    B[i, j] = sum / norm
                else:
                    print('sth went wrong')
    '''
    
    
    # Calculate bear spectrum
    b = np.sum(B, axis=0) / n
    b = b / b[0]
    
    # Valid part of b
    b_valid = b[0:3*len(b)//4]
    l = len(b_valid)
    
    # Initialize J array
    J = np.zeros(l // 3)
    
    # Calculate p using the described algorithm
    for j in range(1, l // 3 + 1):
        delta1 = j
        delta2 = math.floor(3 * j / 4)
        I = 0
        for i in range(j, l, j):
            h1 = np.argmax(b[i-delta1: i+delta1+1]) + max(0, i-delta1)
            h2 = np.argmax(b[i-delta2:  i+delta2+1]) + max(0, i-delta2)
            sum_ = np.sum(b[i-delta2: i+delta2+1])
            if h1 == h2:
                I += b[h1] - sum_ / ((2 * delta2) + 1)
        J[j-1] = I / math.floor(l / j)
    
    # Repeating period
    p = np.argmax(J) + 1
    
    # Repeating segment model
    r = V.shape[1] // p
    S = np.zeros((int(n), int(p * r)))
    
    for i in range(int(n)):
        for l in range(p):
            values_at_l = [V[i, l + k * p] for k in range(r-1)]
            S[i, l] = np.median(values_at_l)
    
    # Compute repeating spectrogram model
    W = np.zeros(V.shape)
    for i in range(int(n)):
        for l in range(p):
            for k in range(r):
                idx = l + k * p
                if idx < V.shape[1]:
                    W[i, idx] = np.minimum(S[i, l], V[i, idx])
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Calculating soft mask, check how they do it I think some thing is wrong here
    M = np.zeros((int(n), m))
    for i in range(int(n-1)):
        for j in range(m-1):
            M[i, j] = W[i, j] / V[i, j] if V[i, j] != 0 else 0
    
    # Ensure mask values are within [0, 1], I deleted this part to see the difference
    
    # Apply mask to STFT
    TempX = np.multiply(M, X)
    
    return TempX

