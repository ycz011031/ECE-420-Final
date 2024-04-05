from imports import *

def pitch_synth (epoch_marks_orig,F_s, audio_data,F_new):
    N = len(audio_data)
    new_epoch_spacing = int(F_s//F_new)
    audio_out = np.zeros(N)
    epoch_mark = 0
    itr = 0
    epoch_marks_orig = np.insert(epoch_marks_orig,0,0)
    for i in range(0, N, new_epoch_spacing):
        itr = find_map(i,epoch_marks_orig,epoch_mark,epoch_marks_orig)
        epoch_mark = itr
        epoch_marks_orig = np.append(epoch_marks_orig,len(audio_data)-1000)
        p0 = int(abs((epoch_marks_orig[itr-1])-(epoch_marks_orig[itr+1]))/2)
        epoch_marks_orig = np.delete(epoch_marks_orig,len(epoch_marks_orig)-1)
        window = np.hanning(p0*2)
        left_idx = int(epoch_marks_orig[itr]-p0)
        right_idx = int(epoch_marks_orig[itr]+p0)
        windowed_sample = window_apply(audio_data[left_idx:right_idx] ,window)
        #print(i-p0)
        sample_addition(audio_out,windowed_sample,i-p0)
    return audio_out



def find_map (new_epoch, epoc_org, epoch_mark,epoch_marks_orig):
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
        if (start+x >= len(a)):
            break
        if (start+x >=0):
            a[start+x]+=b[x]
    return


