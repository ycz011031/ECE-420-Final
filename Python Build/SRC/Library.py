from imports import *

#############################--Epoch Locator--#########################
#Main
def findEpochLocations(audio_data,periodlen):
    epoch_location =[]
    min_idx = int(0)
    max_idx = int(0)

    largestPeak = findMaxArrayIdx(audio_data,0,len(audio_data))
    epoch_location.append(largestPeak)
    epochCandidateIdx = epoch_location[0] + periodlen

    while (epochCandidateIdx < len(audio_data)):
        epoch_location.append(epochCandidateIdx)
        epochCandidateIdx += periodlen
        
    epochCandidateIdx = epoch_location[0] - periodlen
    while (epochCandidateIdx > 0):
        epoch_location.append(epochCandidateIdx)
        epochCandidateIdx -= periodlen

    epoch_location.sort()
    for i in range (len(epoch_location)-1):
        min_idx = int(epoch_location[i] - periodlen/3)
        max_idx = int(epoch_location[i] + periodlen/3)
        peakoffset = findMaxArrayIdx(audio_data,min_idx,max_idx)
        offset = -(epoch_location[i] - peakoffset)
        epoch_location[i] = peakoffset
        if (i < len(epoch_location)-1):
            epoch_location[i+1] += offset
        if (i>0):
            delta = epoch_location[i] - epoch_location[i-1]
            if (delta < periodlen/2.5):
                epoch_location[i] = 9999999
    
    epoch_location.sort()
    epochs_clean_up(epoch_location,len(audio_data))

    return epoch_location

#Helper Function
def findMaxArrayIdx(array, min_idx,max_idx):
    ret_idx = min_idx
    for i in range(min_idx,max_idx):      
        if (array[i] > array[ret_idx]):
            ret_idx = i
    return ret_idx


def epochs_clean_up (array,frame_length):
    if(array[0] < 0):
        array.pop(0)

    i = len(array)-1
    
    while (i>=0):
        if(array[i] >= frame_length):
            array.pop(i)
            i-=1
        else:
            break
    return
#########################################################################




#########################--Frequncy detector--##########################
#Main
def freq_detect(frame, Fs):
    FRAME_SIZE = len(frame)
    threshold = (1800000000/2048)*FRAME_SIZE
    freq = 60
    E = getEnergy(frame)

    if (E<threshold):
        return freq

    R = get_autocor_(frame,E)
    st_pt =  int(Fs/60)  
    sp_pt =  int(Fs/270)
    peaks = peak_detection(R)
    freq = Fs/peak_select(st_pt,sp_pt,peaks)

    return freq

#Helper function
def getEnergy(frame):
    E = int(0)
    for i in range (len(frame)):
        E = E+(frame[i]*frame[i])
    return int(E)

def cycle (a,b):
    if (a<0):
        return a+b
    else:
        return a
    
def get_autocor(frame,E):
    R = []
    for i in range (len(frame)):
        Rl = 0
        for k in range (len(frame)):
            itr = cycle (k-i,len(frame))
            Rl += frame[k] * frame[itr]
        R.append(Rl/E)
    return R

def peak_detection(frame):
    peaks = []
    N = len(frame)
    a = 25
    for i in range(a,N-a):
        if frame[i]>frame[i-a]:
            if frame[i]>=frame[i+a]:
                position = i
                peaks.append(position)
    return peaks

def get_autocor_(frame,E):
    N = np.fft.fft(frame)
    N_ = np.conjugate(N)
    output = np.fft.ifft(N*N_)/E
    return output


def peak_select(st_pt,sp_pt,peaks):
    for i in range (len(peaks)):
        if (peaks[i] < st_pt):
            if(peaks[i]>sp_pt):
                return peaks[i]
    return 60
##########################################################################


############################--Pitch Synthesizor--########################
#Main
def pitch_synth (epoch_marks_orig,F_s, audio_data,F_new):
    N = len(audio_data)
    new_epoch_spacing = int(F_s//F_new)
    audio_out = np.zeros(N)
    epoch_mark = 0
    itr = 0
    epoch_marks_orig = np.insert(epoch_marks_orig,0,0)
    for i in range(0, N, new_epoch_spacing):
        itr = find_map(i,epoch_marks_orig,epoch_mark,epoch_marks_orig)
        epoch_mark = itr
        epoch_marks_orig = np.append(epoch_marks_orig,len(audio_data)-1000)
        p0 = int(abs((epoch_marks_orig[itr-1])-(epoch_marks_orig[itr+1]))/2)
        epoch_marks_orig = np.delete(epoch_marks_orig,len(epoch_marks_orig)-1)
        window = np.hanning(p0*2)
        left_idx = int(epoch_marks_orig[itr]-p0)
        right_idx = int(epoch_marks_orig[itr]+p0)
        windowed_sample = window_apply(audio_data[left_idx:right_idx] ,window)
        sample_addition(audio_out,windowed_sample,i-p0)
    return audio_out

#Helper function
def find_map (new_epoch, epoc_org, epoch_mark,epoch_marks_orig):
    itr = epoch_mark
    delta_min = 0
    for k in range (epoch_mark,len(epoc_org)):
        if (k == epoch_mark):
            delta_min = abs(new_epoch - epoch_marks_orig[k])    
        else:
            delta_new = abs(new_epoch - epoch_marks_orig[k])
            if (delta_new <= delta_min):
                delta_min = delta_new
                itr = k
            else:
                break
    return itr

def window_apply (a,b):
    output = []  
    for j in range(len(a)):
        result = a[j]*b[j]
        output.append(result)
    return output

def sample_addition(a,b,start):
    for x in range(len(b)-1):
        if (start+x >= len(a)):
            break
        if (start+x >=0):
            a[start+x]+=b[x]
    return
##########################################################################


############################--REPET Functions--###########################
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
############################################################################


##########################--Output Function--###############################
def write_file(audio_data,F_s,file_name):
    path_output = "./test_output"
    file_path=os.path.join(path_output,file_name)
    audio_user_out = np.array(audio_data,dtype=np.int16)
    scipy.io.wavfile.write(file_path,F_s,audio_user_out)
############################################################################


#########################--Vocal Detection--################################
def detect_vocals(audio_data,frame_size):
    num_frame = int(len(audio_data)/frame_size)
    active_frame = []
    for i in range(num_frame-1):
        frame = audio_data[i*frame_size:(i+1)*frame_size]
        if check_E(frame):
            active_frame.append(i)
    return active_frame

def check_E (frame):
    threshold = (1800000000/2048)*len(frame)
    E = int(0)
    for i in range (len(frame)):
        E = E+(frame[i]*frame[i])
    if (E>=threshold):
        return True
    else:
        return False