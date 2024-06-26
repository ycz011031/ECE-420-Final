//
// Created by daran on 1/12/2017 to be used in ECE420 Sp17 for the first time.
// Modified by dwang49 on 1/1/2018 to adapt to Android 7.0 and Shield Tablet updates.
//
#include "ece420_lib.h"
#include <jni.h>
#include <cmath>
#include <iostream>
#include <vector>
#include <algorithm>
#include <android/log.h>

// https://en.wikipedia.org/wiki/Hann_function
float getHanningCoef(int N, int idx) {
    return (float) (0.5 * (1.0 - cos(2.0 * M_PI * idx / (N - 1))));
}

int findMaxArrayIdx(float *array, int minIdx, int maxIdx) {
    int ret_idx = minIdx;

    for (int i = minIdx; i < maxIdx; i++) {
        if (array[i] > array[ret_idx]) {
            ret_idx = i;
        }
    }

    return ret_idx;
}

int findClosestIdxInArray(float *array, float value, int minIdx, int maxIdx) {
    int retIdx = minIdx;
    float bestResid = abs(array[retIdx] - value);

    for (int i = minIdx; i < maxIdx; i++) {
        if (abs(array[i] - value) < bestResid) {
            bestResid = abs(array[i] - value);
            retIdx = i;
        }
    }

    return retIdx;
}

// TODO: These should really be templatized
int findClosestInVector(std::vector<int> vec, float value, int minIdx, int maxIdx) {
    int retIdx = minIdx;
    float bestResid = abs(vec[retIdx] - value);

    for (int i = minIdx; i < maxIdx; i++) {
        if (abs(vec[i] - value) < bestResid) {
            bestResid = abs(vec[i] - value);
            retIdx = i;
        }
    }

    return retIdx;
}


float findMaxinVector(std::vector<float> vec, size_t minIdx, size_t maxIdx){
    float output = 0;
    for (size_t i = minIdx; i < maxIdx; i++){
        if(output <= vec[i]){
            output = vec[i];
        }
    }
    return output;
}


float findMininVector(std::vector<float> vec, size_t minIdx, size_t maxIdx){
    float output = vec[minIdx];
    for (size_t i = minIdx; i<maxIdx;i++){
        if(output >= vec[i]){
            output = vec[i];
        }
    }
    return output;
}



float sumofVecotr(std::vector<float> vec, size_t minIdx, size_t maxIdx){
    float output = 0;
    for (size_t i = minIdx; i< maxIdx; i++){
        output += vec[i];
    }
    return output;
}

float findMedian(std::vector<float>& data, int minIdx, int maxIdx) {
    if (minIdx > maxIdx || minIdx < 0 || maxIdx >= data.size()) {
        throw std::invalid_argument("Invalid index range.");
    }

    int n = maxIdx - minIdx + 1;
    int midIdx = minIdx + n / 2;

    std::nth_element(data.begin() + minIdx, data.begin() + midIdx, data.begin() + maxIdx + 1);

    if (n % 2 != 0) {
        return data[midIdx];
    } else {
        float next = *std::min_element(data.begin() + midIdx + 1, data.begin() + maxIdx + 1);
        return (data[midIdx] + next) / 2.0;
    }
}


size_t findMaxIndex(const std::vector<float>& vec, size_t start, size_t end) {
    // Ensure the range is within the bounds of the vector
    float max = findMaxinVector(vec,start,end);
    for (size_t i = 0; i<vec.size(); i++){
        if (max == vec[i]){
            return i;
        }
    }
    return 0;
}


std::vector<std::vector<std::complex<float>>>reverseindex_complex(std::vector<std::vector<std::complex<float>>> source){
    std::vector<std::vector<std::complex<float>>> output;
    output.resize(source[0].size());
    for (size_t i =0; i<source[0].size();i++){
        output[i].resize(source.size());
        for (size_t j = 0; j<source.size();j++){
            output[i][j] = source[j][i];
        }
    }
    return output;
}

std::vector<float> generateSineWave(float frequency, float samplingRate, float duration) {
    std::vector<float> sineWave;
    int totalSamples = static_cast<int>(samplingRate * duration);
    for (int i = 0; i < totalSamples; ++i) {
        float time = i / samplingRate;
        float value = sin(2 * M_PI * frequency * time);
        sineWave.push_back(value);
    }
    return sineWave;
}