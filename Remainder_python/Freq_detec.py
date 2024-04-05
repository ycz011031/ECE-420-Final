from imports import *



def getEnergy(frame):
    E = int(0)
    #print (type(threshold))
    for i in range (len(frame)):
        #print (E)
        E = E+(frame[i]*frame[i])
    #print (E)
    return int(E)

def cycle (a,b):
    if (a<0):
        return a+b
    else:
        return a
    

def get_autocor(frame,E):
    R = []
    for i in range (len(frame)):
        Rl = 0
        for k in range (len(frame)):
            itr = cycle (k-i,len(frame))
            Rl += frame[k] * frame[itr]
        R.append(Rl/E)
    return R

def peak_detection(frame):
    peaks = []
    N = len(frame)
    a = 25
    for i in range(a,N-a):
        if frame[i]>frame[i-a]:
            if frame[i]>=frame[i+a]:
                position = i
                peaks.append(position)
    return peaks

def get_autocor_(frame,E):
    N = np.fft.fft(frame)
    N_ = np.conjugate(N)
    output = np.fft.ifft(N*N_)/E
    return output


def peak_select(st_pt,sp_pt,peaks):
    for i in range (len(peaks)):
        if (peaks[i] < st_pt):
            if(peaks[i]>sp_pt):
                return peaks[i]
    #print (peaks)
    #print ("Fs =")
    return 60
    



def freq_detect(frame, Fs):
    FRAME_SIZE = len(frame)
    threshold = (1800000000/2048)*FRAME_SIZE

    freq = 60

    E = getEnergy(frame)

    #print( 'debug E type is', type(E))
    
    #print('debug threshold type is', type(threshold))
    if (E<threshold):
        return freq

    R = get_autocor_(frame,E)

    st_pt =  int(Fs/60)  
    sp_pt =  int(Fs/270)
    
    peaks = peak_detection(R)
    freq = Fs/peak_select(st_pt,sp_pt,peaks)

    return freq

