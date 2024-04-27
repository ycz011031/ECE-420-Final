//
// Created by Yicheng Zhou on 4/26/2024.
//

#include <jni.h>

#include "kiss_fft/kiss_fft.h"

extern "C" JNIEXPORT void JNICALL Java_com_manikbora_multiscreenapp_SecondActivity_repet(
        JNIEnv* env, jobject obj, jintArray inputArray, jintArray outputArray1, jintArray outputArray2) {

    // Get the length of the input array
    jsize length = env->GetArrayLength(inputArray);

    // Get the elements of the input array
    jint* input = env->GetIntArrayElements(inputArray, nullptr);

    // Allocate memory for output arrays using JNI
    jint* output1 = new jint[length];
    jint* output2 = new jint[length];

    // Example processing: copy input to both outputs
    memcpy(output1, input, length * sizeof(jint));
    memcpy(output2, input, length * sizeof(jint));

    // Set the result back to Java array objects
    env->SetIntArrayRegion(outputArray1, 0, length, output1);
    env->SetIntArrayRegion(outputArray2, 0, length, output2);

    // Release memory and handle JNI clean-up
    env->ReleaseIntArrayElements(inputArray, input, 0); // Release without copying back changes
    delete[] output1;
    delete[] output2;
}

