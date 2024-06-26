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


def sample_addition_x(a,b,start):
    for x in range(len(b)-1):
        if (start+x >= len(a)):
            break
        if (start+x >=0):
            a[start+x]+=b[x]
    return a
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


def adjust_audio_levels( vocal, user):
    # Calculate the averages of each audio array
    avg_vocal = np.mean(vocal)
    avg_user = np.mean(user)

    output = []

    for i in range(len(user)):
        output.append(int(user[i] * avg_vocal*1.5/avg_user))
    return output





def extract_active_audio(map_array):
    segments = []
    i = 0
    while i < len(map_array):
        if map_array[i] != 0:
            curr_seg = []
            j = i
            while j < len(map_array):
                if map_array[j] != 0:
                    curr_seg.append(j)
                    j += 1
                else:
                    break
        
            segments.append(curr_seg)
            i = j
        
        i += 1
    return segments
    


# input: 
#       idx_2d, [[1,2,3],[5,6]]
#       audio_1d, [frame(1), frame(2), frame(3),....]

# output: frame_2d: [[frame(1)-frame(3)], [frame(5)-frame(6)]]
#Frame_size

def idx_2d_to_frame_2d(idx_2d, audio_1d, Frame_size):
    frame_2d = []

    for subarray in idx_2d:
        localarray = []
        for j in subarray:
            localarray = localarray + list(audio_1d[j*Frame_size: (j+1)*Frame_size])
        frame_2d.append(np.array(localarray))

    return frame_2d


def trim_leading_trailing(map_array):
    segments = []
    cur_segments = []
    start = 0
    start_flag = 0
    for i in range(len(map_array)):
        if (map_array[i] != 0) & (start_flag == 0):
            start = i
            start_flag = 1
        else:
            if (start_flag == 1):
                break
    
    end = 0
    end_flag = 0
    for j in range(len(map_array)):
        itr = len(map_array) - j - 1
        if (map_array[itr] != 0) & (end_flag == 0):
            end = itr
            end_flag = 1
        else:
            if (end_flag ==1):
                break
    
    for k in range(len(map_array)):
        if (k >= start) & (k <= end):
            cur_segments.append(k)
    
    segments.append(cur_segments)

    return segments
            


def find_closest_in_vector(vector, value, min_idx, max_idx):

    # Ensure the indices are within the bounds of the vector
    min_idx = max(0, min_idx)
    max_idx = min(len(vector), max_idx)
    
    # Initialize the minimum difference found and the index of that difference
    min_diff = float(np.inf)
    closest_idx = min_idx

    # Iterate through the specified range
    for i in range(min_idx, max_idx):
        diff = abs(vector[i] - value)
        if diff < min_diff:
            min_diff = diff
            closest_idx = i

    return closest_idx

def lab5_pitch_shift(buffer_in, F_S, FREQ_NEW, FRAME_SIZE,F_s):
    period_len = F_s/freq_detect(buffer_in,F_s)
    freq = F_S / period_len
    print(f"Frequency target: {FREQ_NEW}")
    if period_len > 0:
        print(f"Frequency detected: {freq}")

        epoch_locations = findEpochLocations(buffer_in, period_len)

        new_epoch_spacing = F_S / FREQ_NEW
        new_epoch_idx = 0
        epoch_mark = 0

        buffer_out = np.zeros_like(buffer_in)

        while (new_epoch_idx < FRAME_SIZE * 2):
            itr = find_closest_in_vector(epoch_locations, new_epoch_idx, epoch_mark, len(epoch_locations) - 1)
            epoch_mark = itr

            p0 = abs(epoch_locations[itr - 1] - epoch_locations[itr + 1]) // 2

            # Window generation

            window = np.hanning(p0*2)
            windowed_sample = []
            # Window application
            for z in range(2 * int(p0)):
                windowed_sample.append (window[z] * buffer_in[int(epoch_locations[itr] )- int(p0) + z])

            # Sample localization
            sample_addition(buffer_out, windowed_sample, int(new_epoch_idx - p0))
            new_epoch_idx += new_epoch_spacing

        # Final bookkeeping
        new_epoch_idx -= FRAME_SIZE
        if (new_epoch_idx < FRAME_SIZE):
            new_epoch_idx = FRAME_SIZE

    return buffer_out

def butter_lowpass(cutoff_freq, sampling_freq, order=5):
    nyquist_freq = 0.5 * sampling_freq
    normal_cutoff = cutoff_freq / nyquist_freq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def apply_filter(data, cutoff_freq, sampling_freq, order=5):
    b, a = butter_lowpass(cutoff_freq, sampling_freq, order=order)
    filtered_data = signal.lfilter(b, a, data)
    return filtered_data


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


def find_start(map_,i):
    flag = 0
    for j in range(len(map_)):
        if (map_[j] == i) & (flag ==0):
            return j