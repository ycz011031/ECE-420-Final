from imports import *
from Library import *

Frame_size = 2048
path_input = "./test_audio"

F_s, audio_song  = read(os.path.join(path_input,"test_song_complete.wav"))
F_s, audio_user  = read(os.path.join(path_input,"test_song_user1.wav"))
F_s, audio_voice = read(os.path.join(path_input,"test_song_clear_voice.wav"))

write_file(audio_user,F_s,'output_stage0_user.wav')
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

write_file(audio_data_v,F_s,'output_stage1_voice.wav')
write_file(audio_data_m,F_s,'output_stage1_music.wav')
#stage 1 complete

org_vocal = detect_vocals(audio_data_v,Frame_size)
usr_vocal = detect_vocals(audio_data_u,Frame_size)

num_frame_org = int(len(audio_data_v)/Frame_size)
num_frame_usr = int(len(audio_data_u)/Frame_size)

org_map = np.zeros(num_frame_org)
usr_map = np.zeros(num_frame_usr)

map_mark = 1
for i in range(len(org_vocal)):
    if (i>0):
        prev = org_vocal[i-1]
        if (prev == org_vocal[i]-1):
            org_map[org_vocal[i]]=map_mark
        else:
            map_mark+=1

map_mark = 1
for i in range(len(usr_vocal)):
    if (i>0):
        prev = usr_vocal[i-1]
        if (prev == usr_vocal[i]-1):
            usr_map[usr_vocal[i]]=map_mark
        else:
            map_mark+=1


print(usr_vocal)

plt.plot(org_map)
plt.plot(usr_map)
plt.show()