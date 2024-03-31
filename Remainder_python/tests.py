from imports import *
from Freq_detec import *
from Pitch_change import *
from Epoch_detec import *


def epoch_locator_test():
    epoch_marks_orig = np.load("test_vector_all_voiced_epochs.npy")
    F_s, audio_data = read("test_vector_all_voiced.wav")

    print ('F_s is', F_s)
    print ('audio_data', len(audio_data))

    test_sequence = audio_data[:2048]

    freq = freq_detect(test_sequence.astype(float),F_s)

    print ('freq = ', freq)

    epochs = findEpochLocations(audio_data[:2048].astype(int), F_s/freq)
    print ("calculated epochs = ", epochs)
    print ("provided epochs =", epoch_marks_orig[:10])


    vert = []
    vert_ = []
    for i in range (len(epochs)):
        vert.append(audio_data[int(epochs[i])])

    for i in range (len(epoch_marks_orig[:10])):    
        vert_.append(audio_data[epoch_marks_orig[i]])

    plt.plot(test_sequence.astype(float))
    plt.scatter(epochs,vert,color = 'red')
    plt.scatter(epoch_marks_orig[:10],vert_, color = 'blue')
    plt.show()