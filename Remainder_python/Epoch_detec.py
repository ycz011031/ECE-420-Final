from imports import *

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
        min_idx = int(epoch_location[i] - 50)
        max_idx = int(epoch_location[i] + 50)
        peakoffset = findMaxArrayIdx(audio_data,min_idx,max_idx)
        offset = -(epoch_location[i] - peakoffset)
        epoch_location[i] = peakoffset
        if (i < len(epoch_location)-1):
            epoch_location[i+1] += offset
    
    epochs_clean_up(epoch_location,len(audio_data))

    return epoch_location




def findMaxArrayIdx(array, min_idx,max_idx):
    ret_idx = min_idx
    for i in range(min_idx,max_idx):      
        if (array[i] > array[ret_idx]):
            ret_idx = i
    return ret_idx


def epochs_clean_up (array,frame_length):
    i = len(array)-1
    while (i>=0):
        if(array[i] >= frame_length):
            array.pop(i)
            i-=1
        else:
            break
        print (i)
    return