from imports import *
from Freq_detec import *
from Pitch_change import *
from Epoch_detec import *
from tests import *
from Voice_sep import *





F_s, x = scipy.io.wavfile.read("audio_file.wav")

Music_full = music_voice_sep(F_s,x,2048)



print(Music_full)
Voice_full = x - Music_full
print(Voice_full)
Music_output = np.array(Music_full,dtype=np.int16)
scipy.io.wavfile.write('music.wav',F_s,Music_output)

Voice_output = np.array(Voice_full,dtype=np.int16)
scipy.io.wavfile.write('voice.wav',F_s,Voice_output)


print ('finished')


