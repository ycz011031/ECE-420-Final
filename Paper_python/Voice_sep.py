# input x(signal), N(Number of samples in each Hamming window for STFT)
#output 
import numpy as np;
import scipy
import math

x = np.zeros(10)
N = 100

def autoc(frame):
    fft_frame = np.fft.fft(frame)
    power_spectrum = fft_frame * np.conj(fft_frame)
    autoc = np.abs(np.fft.ifft(power_spectrum))
    
    return autoc


f, t, X = scipy.stft(x, window='hamming', nperseg=N, noverlap=N//2, return_onesided=True) # get stft of x

V = np.abs(X) #magnitude spectrogram V

V_squared = V**2
B = np.zeros_like(V_squared)

# do autocorelation of V_squared row by row, and put it in B
num_rows = V_squared.shape[0]
for i in range(num_rows):
    B[i] = autoc(V_squared[i])


n = N/2 + 1
m = t
# Paper method
'''

for i in range (n):
    for j in range (m):
        sum = 0
        for k in range (m - j + 1):
            if k + j - 1 < m:
                sum = V_squared(i,k)*V_squared(i, k + j - 1)
            else :
                raise Exception("Autoc out of bounds")
    norm = m - j + 1
    if norm > 0:  # Prevent division by zero
        B[i, j] = sum / norm
    else:
        B[i, j] = 1145141919810
'''

#calculate b, bear spectrum
b = np.zeros(m)
b = np.sum(B, axis=0) / n
b = b / b[0]




b_valid = b[0:3*len(b)//4]  # discard the longer 1/4 lag
l = len(b_valid)

#j needs to be defined, and each possible period within b/3

Jarray = np.zeros(N) #Jarray contains alll possible j(period) within the first third of b, but doesn't know how to get js, need to check with prof
J = np.zeros(l/3)
# calculate p using algorithm in paper page 4
for j in Jarray:
    delta2 = math.floor(3j/4)
    delta1 = j # should be one for a bigger neigborhood, need to confirm the exact value
    for i in range(j, len(b), j):
        I = 0
        sum = 0
        h1 = np.argmax(b[max(0, i-delta1): min(len(b), i+delta1)]) + max(0, i-delta1)
        h2 = np.argmax(b[max(0, i-delta2): min(len(b), i+delta2)]) + max(0, i-delta2)
        for k in range(max(0, i-delta2), min(len(b), i+delta2)):
            sum += b[k]
        if h1 == h2:
            I += b[h1] - sum / ((2 * delta2) + 1)
    J[j] = I/math.floor(l/j)
    p = np.argmax(J[j])
    
