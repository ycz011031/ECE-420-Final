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
        if (j >=2):
            delta1 = 2
        else:
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