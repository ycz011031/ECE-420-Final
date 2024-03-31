import numpy as np
from numpy.fft import fft
import matplotlib.pyplot as plt
import scipy.io.wavfile as spwav
#from mpldatacursor import datacursor
import sys

plt.style.use('ggplot')

# Note: this epoch list only holds for "test_vector_all_voiced.wav"
epoch_marks_orig = np.load("test_vector_all_voiced_epochs.npy")
F_s, audio_data = spwav.read("test_vector_all_voiced.wav")
N = len(audio_data)

######################## YOUR CODE HERE ##############################

F_new = 400
new_epoch_spacing = F_s//F_new

#print (epoch_marks_orig)


audio_out = np.zeros(N)
# Suggested loop


#since the mapped epoch on original(index) is non-decreasing
#we only need to start there to find the next map for the next new epoch
def find_map (new_epoch, epoc_org, epoch_mark):
    itr = epoch_mark
    delta_min = 0
    for k in range (epoch_mark,len(epoc_org)):
    
        if (k == epoch_mark):
            delta_min = abs(new_epoch - epoch_marks_orig[k])
            
        else:
            delta_new = abs(new_epoch - epoch_marks_orig[k])
            if (delta_new <= delta_min):
                delta_min = delta_new
                itr = k
            else:
                #print('triggered')
                break
    return itr

def window_apply (a,b):
    output = []
    
    for j in range(len(a)):
        result = a[j]*b[j]
        output.append(result)


    return output

def sample_addition(a,b,start):
    for x in range(len(b)-1):
        if (start+x > 170267):
            break
        a[start+x]+=b[x]
    return
        

epoch_mark = 0
epoch_mark_array = []
itr = 0

debug_epoch_new = []
debug_epoch_map = []
print(len(epoch_marks_orig))
epoch_marks_orig = np.insert(epoch_marks_orig,0,0)

for i in range(0, N, new_epoch_spacing):

    # https://courses.engr.illinois.edu/ece420/lab5/lab/#overlap-add-algorithm
    # Your OLA code here
    itr = find_map(i,epoch_marks_orig,epoch_mark)
    #print ("event a")
    epoch_mark = itr
    debug_epoch_new.append(i)
    debug_epoch_map.append(epoch_marks_orig[itr])

    
    epoch_marks_orig = np.append(epoch_marks_orig,len(audio_data)-1000)

    p0 = int(abs((epoch_marks_orig[itr-1])-(epoch_marks_orig[itr+1]))/2)
    epoch_marks_orig = np.delete(epoch_marks_orig,len(epoch_marks_orig)-1)
    #epoch_marks_orig = np.delete(epoch_marks_orig,0)



    window = np.hanning(p0*2)
    print("debug po = ", p0)
    #print ("event b")

    #print("debug data length", len(audio_data[(epoch_marks_orig[itr-1]):(epoch_marks_orig[itr+1]+1)]))
    
    #print("debug window leangth",len(window))
    
    windowed_sample = window_apply(audio_data[epoch_marks_orig[itr]-p0:epoch_marks_orig[itr]+p0] ,window)
    #print ("event c")

    #audio_out[i-p0:p0+i+1] += windowed_sample
    print("debug audio_out length", len(audio_out))

    sample_addition(audio_out,windowed_sample,i-p0)
    



print ("DEBUG: debug_epoch_new:", debug_epoch_new[:10] )
print ("  ")
print ("  ")
print ("DEBUG: debug_epoch_map:" , debug_epoch_map[:10])
print ("DEBUG: original epoch marks", epoch_marks_orig[:10])
plt.figure()
plt.title('zoomed in audio_out at F_new = 400')
plt.xlabel("sample index")
plt.ylabel("magnitude")
plt.plot(audio_out[100:2100])

plt.figure()
plt.plot(audio_out)
plt.title("entire audio_out at F_new = 400 ")
plt.xlabel("sample index")
plt.ylabel("magnitude")
#plt.plot(audio_data[0:2000])
plt.show()

audio_out = audio_out.astype('int16')
spwav.write('audio_out.wav',F_s,audio_out)
print ('finished')



    
    
           
    
