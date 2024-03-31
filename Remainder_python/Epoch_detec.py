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
        min_idx = int(epoch_location[i] - 30)
        max_idx = int(epoch_location[i] + 30)
        #print ("min_idx is",type(min_idx),min_idx)
        #print (type(max_idx))
        peakoffset = findMaxArrayIdx(audio_data,min_idx,max_idx)
        peakoffset -= 30

        epoch_location[i] += peakoffset
    
    return epoch_location




def findMaxArrayIdx(array, min_idx,max_idx):
    ret_idx = min_idx
    for i in range(min_idx,max_idx):
        
        if (array[i] > array[ret_idx]):
            ret_idx = i
    return ret_idx

