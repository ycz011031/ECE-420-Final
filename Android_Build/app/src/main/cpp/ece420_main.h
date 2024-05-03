//
// Created by daran on 1/12/2017 to be used in ECE420 Sp17 for the first time.
// Modified by dwang49 on 1/1/2018 to adapt to Android 7.0 and Shield Tablet updates.
//

#ifndef ECE420_MAIN_H
#define ECE420_MAIN_H

#include "audio_common.h"
#include "buf_manager.h"
#include "debug_utils.h"

int detectBufferPeriod(float *buffer, float* bufferIn);
void findEpochLocations(std::vector<int> &epochLocations, float *buffer, int periodLen, float *bufferIn);
void overlapAddArray(float *dest, float *src, int startIdx, int len);
bool PitchShift(float *bufferIn, float *bufferOut);
void ProcessFrame(int *dataBuf, int* dataOut, float* bufferIn, float* bufferOut);
void Tune_Main(int *input1, int *input2, int *output,int length);

#endif //ECE420_MAIN_H
