# input x(signal), N(Number of samples in each Hamming window for STFT)
#output 
import numpy as np;
import scipy
import math

F_s, x = scipy.io.wavfile.read("test_vector_all_voiced.wav")
N = 2048

def autoc(frame):
    fft_frame = np.fft.fft(frame)
    power_spectrum = fft_frame * np.conj(fft_frame)
    autoc = np.abs(np.fft.ifft(power_spectrum))
    
    return autoc


f, t, X = scipy.signal.stft(x, window='hamming', nperseg=N, noverlap=N//2) # get stft of x

V = np.abs(X) #magnitude spectrogram V

V_squared = V**2
B = np.zeros_like(V_squared)

# do autocorelation of V_squared row by row, and put it in B
num_rows = V_squared.shape[0]
for i in range(num_rows):
    B[i] = autoc(V_squared[i])

m = len(t)
n = N/2 + 1
# Paper method
'''

for i in range (1, n + 1):
    for j in range (1, m + 1):
        sum = 0
        for k in range (1, m - j + 2):
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
J = np.zeros(l//3)
# calculate p using algorithm in paper page 4
for j in range(1, l // 3 + 1):  # Starting from 1 to avoid division by zero
    delta1 = j  # Assuming a neighborhood size based on 'j', adjust if necessary
    delta2 = math.floor(3 * j / 4)
    I = 0 
    for i in range(j, l, j):
        sum_ = 0
        h1 = np.argmax(b[i-delta1: i+delta1+1]) + max(0, i-delta1)
        h2 = np.argmax(b[i-delta2:  i+delta2+1]) + max(0, i-delta2)
        for k in range(i-delta2, i+delta2+1):
            sum_ += b[k]
        if h1 == h2:
            I += b[h1] - sum_ / ((2 * delta2) + 1)
    J[j-1] = I / math.floor(l / j)

# Find the index of the maximum score in 'J', which corresponds to the estimated period 'p'
p = np.argmax(J) + 1 # repeating period


r = V.shape[1] // p # segments of p in V
print(V.shape[1])
print(r)
print(p)
print(r*p)
S = np.zeros((int(n), int(p*r))) #repeating segment model
'''
for i in range (n):
    segments = np.zeros((r, p))
    for k in range(r):
        segments[k, :] = V[i, k*p:(k+1)*p]
    S[i, :] = np.median(segments, axis=0)
'''

for i in range(int(n)):  # Iterate over each frequency bin
    for l in range(p):  # For each position within the period
        values_at_l = [V[i, l + k * p] for k in range(r-1)]
        # Compute the median of these values and assign to S
        S[i, l] = np.median(values_at_l)

W = np.zeros(V.shape) #repeating spectrogram model
for i in range (int(n)):
    for l in range (p):
        for k in range (r):
            idx = l + k * p
            if idx < V.shape[1]:  
                W[i, idx] = np.minimum(S[i, l], V[i, idx])
            else:
                print('out of bounds in W processing')

M = np.zeros((int(n),m)) # calculating soft mask
for i in range(int(n-1)):
    for j in range(m-1):
        if V[i, j] != 0:
            M[i, j] = W[i, j] / V[i, j]
        else:
            M[i, j] = 0
        if (M[i,j] > 1):
            print('M[i,j] > 1', M[i,j])
        if (M[i,j] < 0):
            print('M[i,j] < 0', M[i,j])


if M.shape[0] % 2 == 0:
    # M includes the Nyquist bin, exclude it from the mirror part
    M_mirror = M[-2:0:-1, :]  # Exclude the first (DC) and last (Nyquist) bins
else:
    # M does not include the Nyquist bin
    M_mirror = M[-1:0:-1, :]  # Exclude only the first (DC) bin
    
    # Concatenate M and its mirror image to form the symmetrical mask
M_sym = np.vstack((M, M_mirror))

TempX = np.multiply(M, X)
t2, Music = scipy.signal.istft(TempX, fs=F_s, window='hamming', nperseg=N, noverlap=N//2)
if len(Music) != len(x):
    Music = np.resize(Music, len(x))
print(x)

print(Music)


print(euclidean_distance)
Music_output = np.array(Music,dtype=np.int16)
scipy.io.wavfile.write('music.wav',F_s,Music_output)

Voice_output = np.array(Voice,dtype=np.int16)
scipy.io.wavfile.write('voice.wav',F_s,Music_output)


print ('finished')