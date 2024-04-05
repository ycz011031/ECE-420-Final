from imports import *
from Freq_detec import *
from Pitch_change import *
from Epoch_detec import *
from tests import *
from Voice_sep import *


Frame_size = 2048

#reading input audios
F_s, audio_song  = read("test_song_complete.wav")
F_s, audio_user_ = read("test_song_user.wav")
F_s, audio_voice = read("test_song_clear_voice.wav")

print("Read file complete, F_s is", F_s)

#adjusting the sampling frequency by double sampling the similated user input
audio_user = []
for i in range(len(audio_user_)):
    audio_user.append(audio_user_[i])
    audio_user.append(audio_user_[i])

audio_user_out = np.array(audio_user,dtype=np.int16)
scipy.io.wavfile.write('output_stage0_user.wav',F_s,audio_user_out)


#stage 1, music and voice seperation
audio_music_sep = music_voice_sep(F_s,audio_song,Frame_size)
audio_voice_sep = audio_song - audio_music_sep

audio_data_v = []
audio_data_m = []
audio_data_u = np.array(audio_user,dtype=float)


print(audio_data_u.shape)

if(len(audio_music_sep.shape) > 1):
    for i in range(len(audio_music_sep)):
        audio_data_v.append((audio_voice_sep[i][0] + audio_voice_sep[i][1] )/2)
        audio_data_m.append((audio_music_sep[i][0] + audio_music_sep[i][1] )/2)
        #audio_data_u.append((audio_user[i][0] + audio_user[i][1] )/2)
print ("Song data processing complete")

audio_data_v_out = np.array(audio_data_v,dtype=np.int16)
scipy.io.wavfile.write('output_stage1_voice.wav',F_s,audio_data_v_out)

audio_data_m_out = np.array(audio_data_m,dtype=np.int16)
scipy.io.wavfile.write('output_stage1_music.wav',F_s,audio_data_m_out)
#stage 1 complete


#stage 2 tempral adjustment to user inputs
numFrames_org = int(len(audio_data_v)/Frame_size)
numFrames_usr = int(len(audio_data_u)/Frame_size)

fraction_co = find_closest_fraction(numFrames_org/numFrames_usr)
#print ('debug the fractions are', fraction_co[0], fraction_co[1])
#print (numFrames_org,numFrames_usr)

audio_user_adj = signal.resample_poly(audio_data_u.astype('float'), fraction_co[0], fraction_co[1])
audio_user_adj_out = np.array(audio_user_adj,dtype=np.int16)
scipy.io.wavfile.write('output_stage2_adjusted.wav',F_s,audio_user_adj_out)

#stage 2 complete


#stage 3 pitch correction to user inputs
notes = []
audio_user_syth =[]

for i in range(numFrames_org):
    frame_ = audio_data_v[i*Frame_size:(i+1)*Frame_size]
    frame = np.array(frame_,dtype=np.int16)
    freq = freq_detect(frame.astype(float),F_s)
    notes.append(freq)
print ("notes generated")



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

def lab5_pitch_shift(buffer_in, F_S, FREQ_NEW, FRAME_SIZE):
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





#after resampling, there is still a slight mismatch in length from the target and user, here we select the shorter one as base to avoid seg fault
numFrames_usr = int(len(audio_user_adj)/Frame_size)

if (numFrames_org<numFrames_usr):
    numFrames = numFrames_org
else:
    numFrames = numFrames_usr

buffer = np.zeros(3*Frame_size)
epochs1 = [0]
epochs2 = []
epochs3 = []

for k in range(numFrames-1):

    frame = audio_user_adj[k*Frame_size:(k+1)*Frame_size]
    buffer[Frame_size*2:Frame_size*3] = frame
    freq = freq_detect(buffer.astype(float),F_s)
    epochs1 = findEpochLocations(frame.astype(float), F_s/freq)
    target_freq = notes[k]
    epochs = epochs1 + epochs2 + epochs3
    epochs.sort()
    #print(epochs)
    #audio_out_ = lab5_pitch_shift(buffer, F_s, target_freq, Frame_size)
    #audio_out_ = pitch_synth (epochs,F_s, buffer,target_freq)
    audio_out_ = pitch_synth (epochs1,F_s, frame,target_freq)
    for j in range (Frame_size):
        #audio_user_syth.append(audio_out_[Frame_size*2+j])
        audio_user_syth.append(audio_out_[j])

    #print(buffer[Frame_size:Frame_size*2])
    buffer[Frame_size:Frame_size*2] = buffer[Frame_size*2:Frame_size*3]
    buffer[0 : Frame_size] = buffer[Frame_size:Frame_size*2]
    epochs3 = [x + Frame_size for x in epochs2]
    epochs2 = [x + Frame_size for x in epochs1]


apply_filter(audio_user_syth, 5000, F_s, order=5)


audio_user_adj_syth_out = np.array(audio_user_syth,dtype=np.int16)
scipy.io.wavfile.write('output_stage3_synthesized.wav',F_s,audio_user_adj_syth_out)


data_fd = np.fft.fft(audio_user_adj_syth_out)
freq_i = np.fft.fftfreq(len(audio_user_adj_syth_out),d=1/F_s)



audio_output = sample_addition(audio_data_m_out,audio_user_adj_syth_out,0)

#audio_output_final = np.array(audio_output,dtype=np.int16)
scipy.io.wavfile.write('output_final_synthesized.wav',F_s,audio_data_m_out)



quit()


audio_data_m_o = np.array(audio_data_m,dtype=np.int16)
scipy.io.wavfile.write('music.wav',F_s,audio_data_m_o)

Voice_output = np.array(Voice_full,dtype=np.int16)
scipy.io.wavfile.write('voice.wav',F_s,Voice_output)

audio_output = np.array(audio_out,dtype=np.int16)
    #audio_output = audio_output.astype(int16)
spwav.write('audio_out.wav',F_s,audio_output)
print ('debug audio_out shape', audio_output.shape)

print ('finished')


