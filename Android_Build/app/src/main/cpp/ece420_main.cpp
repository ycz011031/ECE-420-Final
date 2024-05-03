//
// Created by daran on 1/12/2017 to be used in ECE420 Sp17 for the first time.
// Modified by dwang49 on 1/1/2018 to adapt to Android 7.0 and Shield Tablet updates.
//

#include <jni.h>
#include <vector>
#include "ece420_main.h"
#include "ece420_lib.h"
#include "kiss_fft/kiss_fft.h"

// JNI Function
extern "C" {
JNIEXPORT void JNICALL
Java_com_ece420_lab5_MainActivity_writeNewFreq(JNIEnv *env, jclass, jint);
}

// Student Variables
#define EPOCH_PEAK_REGION_WIGGLE 30
#define VOICED_THRESHOLD 2000
#define FRAME_SIZE 1024
#define BUFFER_SIZE (3 * FRAME_SIZE)
#define F_S 48000

//float bufferOut[BUFFER_SIZE] = {};
int newEpochIdx = FRAME_SIZE;

// We have two variables here to ensure that we never change the desired frequency while
// processing a frame. Thread synchronization, etc. Setting to 300 is only an initializer.
int FREQ_NEW_ANDROID = 300;
int FREQ_NEW = 300;

bool PitchShift(float *bufferIn, float *bufferOut) {
    int periodLen = detectBufferPeriod(bufferIn,bufferIn);
    //float freq = ((float) F_S) / periodLen;

    // If voiced
    if (periodLen > 0) {
        // Epoch detection - this code is written for you, but the principles will be quizzed
        std::vector<int> epochLocations;
        findEpochLocations(epochLocations, bufferIn, periodLen,bufferIn);
                // *********************** START YOUR CODE HERE  **************************** //
        int new_epoch_spacing = F_S/FREQ_NEW;
        int epoch_mark = 0;

        //removing duplicates in epochlocations
        //auto target = std::unique(epochLocations.begin(),epochLocations.end());
        //epochLocations.erase(target);

        //getting new epoch locations
        while (newEpochIdx < FRAME_SIZE*2){
        //for (newEpochIdx; newEpochIdx<FRAME_SIZE*2; newEpochIdx+=new_epoch_spacing){
            auto itr = findClosestInVector(epochLocations,newEpochIdx,epoch_mark,(epochLocations).size()-1);
            epoch_mark = itr;

            auto p0 = abs(epochLocations[itr-1] - epochLocations[itr+1])/2;

            //window generation
            std::vector<float> window((int)p0*2);
            for (int y=0; y<2*p0+1;y++){
                window[y] = getHanningCoef(p0*2,y);
            }

            //window application
            std::vector<float> windowed_sample(2*(int)p0+1);
            for (int z=0;z<2*p0;z++){
                int ptr = epochLocations[itr]-p0+z;
                windowed_sample[z] = window[z]*bufferIn[ptr];
            }

            //sample localization
            overlapAddArray(bufferOut,windowed_sample.data(),newEpochIdx-p0,2*p0);
            newEpochIdx+=new_epoch_spacing;
        }

        // ************************ END YOUR CODE HERE  ***************************** //
    }

    // Final bookkeeping, move your new pointer back, because you'll be
    // shifting everything back now in your circular buffer
    newEpochIdx -= FRAME_SIZE;
    if (newEpochIdx < FRAME_SIZE) {
        newEpochIdx = FRAME_SIZE;
    }

    return (periodLen > 0);
}
void overlapAddArray(float *dest, float *src, int startIdx, int len) {
    int idxLow = startIdx;
    int idxHigh = startIdx + len;

    int padLow = 0;
    int padHigh = 0;
    if (idxLow < 0) {
        padLow = -idxLow;
    }
    if (idxHigh > BUFFER_SIZE) {
        padHigh = BUFFER_SIZE - idxHigh;
    }

    // Finally, reconstruct the buffer
    for (int i = padLow; i < len + padHigh; i++) {
        dest[startIdx + i] += src[i];
    }
}
void findEpochLocations(std::vector<int> &epochLocations, float *buffer, int periodLen, float *bufferIn) {
    // This algorithm requires that the epoch locations be pretty well marked

    int largestPeak = findMaxArrayIdx(bufferIn, 0, BUFFER_SIZE);
    epochLocations.push_back(largestPeak);

    // First go right
    int epochCandidateIdx = epochLocations[0] + periodLen;
    while (epochCandidateIdx < BUFFER_SIZE) {
        epochLocations.push_back(epochCandidateIdx);
        epochCandidateIdx += periodLen;
    }

    // Then go left
    epochCandidateIdx = epochLocations[0] - periodLen;
    while (epochCandidateIdx > 0) {
        epochLocations.push_back(epochCandidateIdx);
        epochCandidateIdx -= periodLen;
    }

    // Sort in place so that we can more easily find the period,
    // where period = (epochLocations[t+1] + epochLocations[t-1]) / 2
    std::sort(epochLocations.begin(), epochLocations.end());

    // Finally, just to make sure we have our epochs in the right
    // place, ensure that every epoch mark (sans first/last) sits on a peak
    for (int i = 1; i < epochLocations.size() - 1; i++) {
        int minIdx = epochLocations[i] - EPOCH_PEAK_REGION_WIGGLE;
        int maxIdx = epochLocations[i] + EPOCH_PEAK_REGION_WIGGLE;

        int peakOffset = findMaxArrayIdx(bufferIn, minIdx, maxIdx) - minIdx;
        peakOffset -= EPOCH_PEAK_REGION_WIGGLE;

        epochLocations[i] += peakOffset;
    }
}
int detectBufferPeriod(float *buffer, float* bufferIn) {

    float totalPower = 0;
    for (int i = 0; i < BUFFER_SIZE; i++) {
        totalPower += buffer[i] * buffer[i];
    }

    if (totalPower < VOICED_THRESHOLD) {
        return -1;
    }

    // FFT is done using Kiss FFT engine. Remember to free(cfg) on completion
    kiss_fft_cfg cfg = kiss_fft_alloc(BUFFER_SIZE, false, 0, 0);

    kiss_fft_cpx buffer_in[BUFFER_SIZE];
    kiss_fft_cpx buffer_fft[BUFFER_SIZE];

    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer_in[i].r = bufferIn[i];
        buffer_in[i].i = 0;
    }

    kiss_fft(cfg, buffer_in, buffer_fft);
    free(cfg);


    // Autocorrelation is given by:
    // autoc = ifft(fft(x) * conj(fft(x))
    //
    // Also, (a + jb) (a - jb) = a^2 + b^2
    kiss_fft_cfg cfg_ifft = kiss_fft_alloc(BUFFER_SIZE, true, 0, 0);

    kiss_fft_cpx multiplied_fft[BUFFER_SIZE];
    kiss_fft_cpx autoc_kiss[BUFFER_SIZE];

    for (int i = 0; i < BUFFER_SIZE; i++) {
        multiplied_fft[i].r = (buffer_fft[i].r * buffer_fft[i].r)
                              + (buffer_fft[i].i * buffer_fft[i].i);
        multiplied_fft[i].i = 0;
    }

    kiss_fft(cfg_ifft, multiplied_fft, autoc_kiss);
    free(cfg_ifft);

    // Move to a normal float array rather than a struct array of r/i components
    float autoc[BUFFER_SIZE];
    for (int i = 0; i < BUFFER_SIZE; i++) {
        autoc[i] = autoc_kiss[i].r;
    }

    // We're only interested in pitches below 1000Hz.
    // Why does this line guarantee we only identify pitches below 1000Hz?
    int minIdx = F_S / 1000;
    int maxIdx = BUFFER_SIZE / 2;

    int periodLen = findMaxArrayIdx(autoc, minIdx, maxIdx);
    float freq = ((float) F_S) / periodLen;

    // TODO: tune
    if (freq < 50) {
        periodLen = -1;
    }

    return periodLen;
}
int detectBufferFrequency(float *buffer, float* bufferIn) {

//
//    float totalPower = 0;
//    for (int i = 0; i < BUFFER_SIZE; i++) {
//        totalPower += buffer[i] * buffer[i];
//    }
//
//
//    if (totalPower < VOICED_THRESHOLD) {
//        return -1;
//    }

    // FFT is done using Kiss FFT engine. Remember to free(cfg) on completion
    kiss_fft_cfg cfg = kiss_fft_alloc(BUFFER_SIZE, false, 0, 0);

    kiss_fft_cpx buffer_in[BUFFER_SIZE];
    kiss_fft_cpx buffer_fft[BUFFER_SIZE];

    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer_in[i].r = bufferIn[i];
        buffer_in[i].i = 0;
    }

    kiss_fft(cfg, buffer_in, buffer_fft);
    free(cfg);


    // Autocorrelation is given by:
    // autoc = ifft(fft(x) * conj(fft(x))
    //
    // Also, (a + jb) (a - jb) = a^2 + b^2
    kiss_fft_cfg cfg_ifft = kiss_fft_alloc(BUFFER_SIZE, true, 0, 0);

    kiss_fft_cpx multiplied_fft[BUFFER_SIZE];
    kiss_fft_cpx autoc_kiss[BUFFER_SIZE];

    for (int i = 0; i < BUFFER_SIZE; i++) {
        multiplied_fft[i].r = (buffer_fft[i].r * buffer_fft[i].r)
                              + (buffer_fft[i].i * buffer_fft[i].i);
        multiplied_fft[i].i = 0;
    }

    kiss_fft(cfg_ifft, multiplied_fft, autoc_kiss);
    free(cfg_ifft);

    // Move to a normal float array rather than a struct array of r/i components
    float autoc[BUFFER_SIZE];
    for (int i = 0; i < BUFFER_SIZE; i++) {
        autoc[i] = autoc_kiss[i].r;
    }

    // We're only interested in pitches below 1000Hz.
    // Why does this line guarantee we only identify pitches below 1000Hz?
    int minIdx = F_S / 1000;
    int maxIdx = BUFFER_SIZE / 2;

    int periodLen = findMaxArrayIdx(autoc, minIdx, maxIdx);
    float freq = ((float) F_S) / periodLen;

    // TODO: tune
    return freq;
}



void ProcessFrame(int *dataBuf, int* dataOut, float* bufferIn, float* bufferOut) {
    // Shift our old data back to make room for the new data
    for (int i = 0; i < 2 * FRAME_SIZE; i++) {
        bufferIn[i] = bufferIn[i + FRAME_SIZE - 1];
    }

    // Finally, put in our new data.
    for (int i = 0; i < FRAME_SIZE; i++) {
        bufferIn[i + 2 * FRAME_SIZE - 1] = (float) dataBuf[i];
    }

    // The whole kit and kaboodle -- pitch shift
    bool isVoiced = PitchShift(bufferIn,bufferOut);

    for (int i =0; i<FRAME_SIZE; i++){
        if (isVoiced){
            dataOut[i] = bufferOut[FRAME_SIZE+i];
        }
        else {
            dataOut[i] = 0;
        }
    }

    // Very last thing, update your output circular buffer!
    for (int i = 0; i < 2 * FRAME_SIZE; i++) {
        bufferOut[i] = bufferOut[i + FRAME_SIZE - 1];
    }

    for (int i = 0; i < FRAME_SIZE; i++) {
        bufferOut[i + 2 * FRAME_SIZE - 1] = 0;
    }

    return;
}


void Tune_Main(int *input1, int *input2, int *output,int length){
    int num_of_frame = length/FRAME_SIZE;
    float bufferIn[BUFFER_SIZE] = {};
    float bufferOut[BUFFER_SIZE] = {};
    int dataBuf[FRAME_SIZE] = {};
    int dataOut[FRAME_SIZE] = {};
    float dataVoc[FRAME_SIZE] = {};
    int ptr = 0;

    for (int i = 0; i < num_of_frame; i++){
        for (int j=0; j<FRAME_SIZE; j++){
            dataBuf[j] = input1[ptr*i+j];
            dataVoc[j] = static_cast<float>(input2[ptr*i+j]);
        }

        FREQ_NEW = detectBufferFrequency(dataVoc,dataVoc);
        ProcessFrame(dataBuf,dataOut,bufferIn,bufferOut);

        for (int k=0;k<FRAME_SIZE;k++){
            output[ptr+k] = 3*dataOut[k];
        }


    }
    return;
}





extern "C" JNIEXPORT void JNICALL Java_com_manikbora_multiscreenapp_ThirdActivity_tune(JNIEnv *env, jobject obj, jintArray array1, jintArray array2, jintArray array3) {
    jint *elements1 = env->GetIntArrayElements(array1, 0);
    jint *elements2 = env->GetIntArrayElements(array2, 0);
    jint *elements3 = env->GetIntArrayElements(array3, 0);
    jsize length1 = env->GetArrayLength(array2);


    Tune_Main(elements1, elements2, elements3,length1);

    //TO DO Add Main Processing Frame Call

    env->ReleaseIntArrayElements(array1, elements1, 0); // 0 to copy back the changes (if any)
    env->ReleaseIntArrayElements(array2, elements2, 0); // 0 to copy back the changes (if any)
    env->ReleaseIntArrayElements(array3, elements3, 0); // 0 to copy back the changes (if any)
}