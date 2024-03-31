from imports import *
from Freq_detec import *
from Pitch_change import *
from Epoch_detec import *



FRAME_SIZE = 8192
threshold = (1800000000/2048)*FRAME_SIZE

epoch_marks_orig = np.load("test_vector_all_voiced_epochs.npy")
F_s, audio_data = read("test_vector.wav")
N = len(audio_data)


test_sequence = audio_data[:2048]

freq = freq_detect(test_sequence.astype(float),F_s)

print ('freq = ', freq)

epochs = findEpochLocations(audio_data[:2048], F_s/240)
print (epochs)
print (epoch_marks_orig[:10])

print (audio_data[:500].astype(float))


plt.plot(test_sequence.astype(float))
plt.show()