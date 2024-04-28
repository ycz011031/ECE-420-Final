//
// Created by Yicheng Zhou on 4/26/2024.
//

#include <jni.h>
#include <cmath>
#include <iostream>
#include <algorithm>

#include "kiss_fft/kiss_fft.h"


void processAudio(int* input, int* output1, int* output2, int length){

    for (int i=0; i<length; i++){
        output1[i] = input[i];
        output2[length-i-1]  = input[i];
    }
}

extern "C" JNIEXPORT void JNICALL Java_com_manikbora_multiscreenapp_SecondActivity_repet(
        JNIEnv* env, jobject obj, jintArray inputArray, jintArray outputArray1, jintArray outputArray2) {

    // Get the length of the input array
    jsize length = env->GetArrayLength(inputArray);

    // Allocate memory for output arrays using JNI


    jint* input = env->GetIntArrayElements(inputArray,nullptr);
    jint* output1 = env->GetIntArrayElements(outputArray1,nullptr);
    jint* output2 = env->GetIntArrayElements(outputArray2,nullptr);


    // Example processing: copy input to both outputs
    processAudio(input,output1,output2,length);

    // Release memory and handle JNI clean-up
    env->ReleaseIntArrayElements(inputArray, input, 0); // Release without copying back changes
    env->ReleaseIntArrayElements(outputArray1,output1,0);
    env->ReleaseIntArrayElements(outputArray2,output2,0);
}


