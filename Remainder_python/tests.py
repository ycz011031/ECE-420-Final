from imports import *
from Freq_detec import *
from Pitch_change import *
from Epoch_detec import *


def epoch_locator_test(epoch_marks_orig,F_s,test_sequence):

    freq = freq_detect(test_sequence.astype(float),F_s)
    epochs = findEpochLocations(test_sequence.astype(int), F_s/freq)
    Delta = []

    if (len(epochs) != len(epoch_marks_orig)):
        print ('test failed')
        print ("calculated epochs = ", epochs)
        print ("provided epochs =", epoch_marks_orig)
        plot_result(test_sequence,epochs,epoch_marks_orig)
        return


    for i in range (len(epochs)):
        Delta.append(epochs[i] - epoch_marks_orig[i])
    if (sum(Delta) == 0):
        print ('test passed')
        return
    else:
        print ('test failed')
        print ("calculated epochs = ", epochs)
        print ("provided   epochs =", epoch_marks_orig)
        plot_result(test_sequence,epochs,epoch_marks_orig)
        return






def plot_result(test_sequence,epochs,epoch_marks_orig):
    vert = []
    vert_ = []
    for i in range (len(epochs)):
        vert.append(test_sequence[int(epochs[i])])

    for i in range (len(epoch_marks_orig)):    
        vert_.append(test_sequence[epoch_marks_orig[i]])

    plt.plot(test_sequence.astype(float))
    plt.scatter(epochs,vert,color = 'red')
    plt.scatter(epoch_marks_orig,vert_, color = 'blue')
    plt.show()