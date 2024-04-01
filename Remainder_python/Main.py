from imports import *
from Freq_detec import *
from Pitch_change import *
from Epoch_detec import *
from tests import *




#Main()
epoch_marks_orig = np.load("test_vector_all_voiced_epochs.npy")
F_s, audio_data = read("test_vector_all_voiced.wav")
Frame_size = 2048

def test_epoch():
    numFrames = int(len(audio_data)/Frame_size)
    for i in range(numFrames):
        frame = audio_data[i*Frame_size:(i+1)*Frame_size]
        epochs_in = []
        for j in range (len(epoch_marks_orig)):
            if (epoch_marks_orig[j]<Frame_size) & (epoch_marks_orig[j]>=0):
                epochs_in.append(epoch_marks_orig[j])
            epoch_marks_orig[j] -= Frame_size
        
        epoch_locator_test(epochs_in,F_s,frame)





numFrames = int(len(audio_data)/Frame_size)
print(numFrames)

notes= [522/2, 588/2,660/2,698/2,784/2,880/2,988/2,522]
audio_out = []
numFrames = int(len(audio_data)/Frame_size)
for i in range(len(notes)*10):
    frame = audio_data[i*Frame_size:(i+1)*Frame_size]
    indx = int(i/10)
    target_freq = notes[indx]
    freq = freq_detect(frame.astype(float),F_s)
    epochs = findEpochLocations(frame.astype(int), F_s/freq)
    audio_out_ = pitch_synth (epochs,F_s, frame,target_freq)
    for j in range (len(audio_out_)):
        audio_out.append(audio_out_[j])



audio_output = np.array(audio_out,dtype=np.int16)
#audio_output = audio_output.astype(int16)
spwav.write('audio_out.wav',F_s,audio_output)
print ('finished')