//
// Created by daran on 1/12/2017 to be used in ECE420 Sp17 for the first time.
// Modified by dwang49 on 1/1/2018 to adapt to Android 7.0 and Shield Tablet updates.
//

#ifndef ECE420_LIB_H
#define ECE420_LIB_H

#include <math.h>
#include <vector>
#include "kiss_fft/kiss_fft.h"
#include "kiss_fft/kissfft.hh"

float getHanningCoef(int N, int idx);
int findMaxArrayIdx(float *array, int minIdx, int maxIdx);
int findClosestIdxInArray(float *array, float value, int minIdx, int maxIdx);
int findClosestInVector(std::vector<int> vector, float value, int minIdx, int maxIdx);
float findMaxinVector(std::vector<float> vec, size_t minIdx, size_t maxIdx);
float findMininVector(std::vector<float> vec, size_t minIdx, size_t maxIdx);
float sumofVecotr(std::vector<float> vec, size_t minIdx, size_t maxIdx);
float findMedian(std::vector<float>& data, int minIdx, int maxIdx);
size_t findMaxIndex(const std::vector<float>& data, size_t start, size_t end);
std::vector<std::vector<std::complex<float>>>reverseindex_complex(std::vector<std::vector<std::complex<float>>> source);
std::vector<float> generateSineWave(float frequency, float samplingRate, float duration);

#endif //ECE420_LIB_H
