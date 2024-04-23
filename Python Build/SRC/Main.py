from imports import *
from Library import *

Frame_size = 2048
path_input = "./test_audio"

F_s, audio_song  = read(os.path.join(path_input,"test_song_complete.wav"))
F_s, audio_user  = read(os.path.join(path_input,"test_song_user1.wav"))
F_s, audio_voice = read(os.path.join(path_input,"test_song_clear_voice.wav"))


audio_user_out = np.array(audio_user,dtype=np.int16)


#stage 1, music and voice seperation
audio_music_sep = music_voice_sep(F_s,audio_song,Frame_size)
audio_voice_sep = audio_song - audio_music_sep

audio_data_v = []
audio_data_m = []
audio_data_u = []

if(len(audio_music_sep.shape) > 1):
    for i in range(len(audio_music_sep)):
        audio_data_v.append((audio_voice_sep[i][0] + audio_voice_sep[i][1] )/2)
        audio_data_m.append((audio_music_sep[i][0] + audio_music_sep[i][1] )/2)

if(len(audio_user_out.shape) > 1):
    for i in range(len(audio_user_out)):
        audio_data_u.append((audio_user_out[i][0] + audio_user_out[i][1] )/2)
print ("Song data processing complete")

audio_data_u = np.array(audio_data_u,dtype=np.int16)

write_file(audio_data_u,F_s,'output_stage0_user.wav')

write_file(audio_data_v,F_s,'output_stage1_voice.wav')
write_file(audio_data_m,F_s,'output_stage1_music.wav')
#stage 1 complete
audio_data_m_out = np.array(audio_data_m,dtype=np.int16)
audio_data_u = adjust_audio_levels(audio_data_v, audio_data_u)



org_vocal = detect_vocals(audio_data_v,Frame_size) # (number of active frames, song's vocal)
usr_vocal = detect_vocals(audio_data_u,Frame_size) # (number of active frames, user's input)

# ---------------------------- generate maps for song's vocal and user's input ----------------------------
num_frame_org = int(len(audio_data_v)/Frame_size)
num_frame_usr = int(len(audio_data_u)/Frame_size)

org_map = np.zeros(num_frame_org)
usr_map = np.zeros(num_frame_usr)

map_mark_org = 1
for i in range(len(org_vocal)):
    if (i>0):
        prev = org_vocal[i-1]
        if (prev == org_vocal[i]-1):
            org_map[org_vocal[i]]=map_mark_org
        else:
            map_mark_org+=1

map_mark_usr = 1
for i in range(len(usr_vocal)):
    if (i>0):
        prev = usr_vocal[i-1]
        if (prev == usr_vocal[i]-1):
            usr_map[usr_vocal[i]]=map_mark_usr
        else:
            map_mark_usr+=1



print (map_mark_org, ",", map_mark_usr)

if (map_mark_usr == map_mark_org) & (map_mark_usr > 1):
    usr_map_active = extract_active_audio(usr_map) # [0,1,1,1,0,2,2,0] => [[1,2,3],[5,6]]
    org_map_active = extract_active_audio(org_map) # [0,1,1,1,0,2,2,0] => [[1,2,3],[5,6]]
    user_segments  = idx_2d_to_frame_2d(usr_map_active, audio_data_u, Frame_size)
    vocal_segments = idx_2d_to_frame_2d(org_map_active, audio_data_v, Frame_size)
else:
    usr_map_active = trim_leading_trailing(usr_map)
    org_map_active = trim_leading_trailing(org_map)
    user_segments  = idx_2d_to_frame_2d(usr_map_active, audio_data_u, Frame_size)
    vocal_segments = idx_2d_to_frame_2d(org_map_active, audio_data_v, Frame_size)

######################################################################################################################

#stage 2 tempral adjustment to user inputs


print (len(vocal_segments))
print (len(user_segments))

for i in range(len(vocal_segments)):
    numFrames_org = int(len(vocal_segments[i])/Frame_size)
    numFrames_usr = int(len(user_segments[i])/Frame_size)

    fraction_co = find_closest_fraction(numFrames_org/numFrames_usr)
    audio_user_adj = signal.resample_poly(user_segments[i].astype('float'), fraction_co[0], fraction_co[1])

audio_data_u = np.zeros(len(audio_data_v))
for i in range(len(user_segments)):
    start_idx = find_start(org_map,i+1)
    for j in range(len(user_segments[i])):
        audio_data_u[start_idx + j] = user_segments[i][j]

write_file(audio_data_u,F_s,'output_stage2_user_adj.wav')
#stage 2 complete


notes = []
audio_user_syth =[]

for i in range(numFrames_org):
    frame_ = audio_data_v[i*Frame_size:(i+1)*Frame_size]
    frame = np.array(frame_,dtype=np.int16)
    freq = freq_detect(frame.astype(float),F_s)
    notes.append(freq)
print ("notes generated")




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
write_file(audio_user_syth,F_s,'output_stage3_synthesized.wav')

data_fd = np.fft.fft(audio_user_adj_syth_out)
freq_i = np.fft.fftfreq(len(audio_user_adj_syth_out),d=1/F_s)


print(audio_data_m_out)
print(audio_user_adj_syth_out)

audio_output = sample_addition_x(audio_data_m,audio_user_syth,start_idx)
print(audio_output)

write_file(audio_output,F_s,'output_final_synthesized.wav')

