//
// Created by Yicheng Zhou on 4/26/2024.
//

#include <jni.h>
#include <cmath>
#include <iostream>
#include <vector>
#include <algorithm>

#include "kiss_fft/kiss_fft.h"
#include "kiss_fft/kissfft.hh"
#include "ece420_lib.h"



std::vector<float> apply_hanning_window(const std::vector<float>& signal, int start, int size) {
    std::vector<float> windowed(size);
    for (int i = 0; i < size; ++i) {
        windowed[i] = signal[start + i] * 0.5 * (1 - cos(2 * M_PI * i / (size - 1)));
    }
    return windowed;
}

std::vector<kissfft<float>::cpx_type> convert_to_complex(const std::vector<float>& real_signal) {
    std::vector<kissfft<float>::cpx_type> complex_signal(real_signal.size());
    for (size_t i = 0; i < real_signal.size(); ++i) {
        complex_signal[i] = kissfft<float>::cpx_type(real_signal[i], 0); // Convert real to complex
    }
    return complex_signal;
}

void stft(const std::vector<float>& input_signal, int length_of_segment, int number_of_overlaps,std::vector<float>& times, std::vector<std::vector<std::complex<float>>>&  stft_results) {
    int hop_size = length_of_segment - number_of_overlaps;
    kissfft<float> fft(length_of_segment, false); // FFT setup
    std::vector<std::complex<float>> windowed_signal(length_of_segment);
    std::vector<std::complex<float>> spectrum(length_of_segment);
    //std::vector<float> times;
    //std::vector<std::vector<std::complex<float>>> stft_results;  // Store full complex spectrum

    for (int i = 0; i + length_of_segment <= input_signal.size(); i += hop_size) {
        auto real_windowed_signal = apply_hanning_window(input_signal, i, length_of_segment);
        windowed_signal = convert_to_complex(real_windowed_signal);

        // Perform FFT
        fft.transform(windowed_signal.data(), spectrum.data());

        // Store the results
        times.push_back(static_cast<float>(i));
        stft_results.push_back(std::vector<std::complex<float>>(spectrum.begin(), spectrum.end()));  // Copy spectrum to results
    }

    return;
}

std::vector<float> inverseSTFT(const std::vector<std::vector<std::complex<float>>>& inputData, int window_length, int number_of_overlap, int signalLength) {
    int hopSize = window_length - number_of_overlap; // Calculate the hop size from window length and number of overlaps

    // Instantiate the inverse FFT object for the given window length
    kissfft<float> ifft(window_length, true); // true indicates inverse FFT

    // Initialize the output signal with zeros
    std::vector<float> signal(signalLength, 0.0f);

    // Buffer for the output of the inverse FFT
    std::vector<std::complex<float>> timeSegment(window_length);

    // Overlap-add process
    for (size_t i = 0; i < inputData.size(); ++i) {
        int startIdx = i * hopSize;

        // Perform the inverse FFT on the current segment
        ifft.transform(inputData[i].data(), timeSegment.data());

        // Overlap-add method to reconstruct the signal
        for (int j = 0; j < window_length; ++j) {
            if (startIdx + j < signal.size()) {
                signal[startIdx + j] += timeSegment[j].real(); // Assuming a real-valued original signal
            }
        }
    }

    return signal;
}

std::vector<float> autocorrelation(const std::vector<float>& input) {
    int N = input.size();

    // Initialize FFT and iFFT
    kissfft<float> fft(N, false); // false for forward FFT
    kissfft<float> ifft(N, true); // true for inverse FFT

    std::vector<std::complex<float>> input_complex(N);
    std::vector<std::complex<float>> fft_output(N);
    std::vector<std::complex<float>> ifft_output(N);

    // Convert input to complex format and perform FFT
    for (size_t i = 0; i < N; ++i) {
        input_complex[i] = std::complex<float>(input[i], 0);
    }
    fft.transform(input_complex.data(), fft_output.data());

    // Calculate the power spectral density (magnitude squared)
    for (size_t i = 0; i < N; ++i) {
        float mag_sq = std::norm(fft_output[i]);  // Magnitude squared of the FFT output
        fft_output[i] = std::complex<float>(mag_sq, 0);
    }

    // Perform inverse FFT on the power spectral density
    ifft.transform(fft_output.data(), ifft_output.data());

    // Extract the real part of the inverse FFT result and normalize
    std::vector<float> autocorr_result(N);
    for (size_t i = 0; i < N; ++i) {
        autocorr_result[i] = ifft_output[i].real() / N; // Normalizing by the number of samples
    }

    return autocorr_result;
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


void processAudio(int* input, int* output1, int* output2, int length){

    int window_length = 1024;
    int num_overlap = window_length/2;


    std::vector<float> output1_flt(length);
    std::vector<float> output2_flt(length);
    std::vector<float> input_flt(length) ;
    for (int i= 0; i<length; i++){
        input_flt[i] = (float)input[i];
    }


    std::vector<std::vector<std::complex<float>>> stft_out_;
    std::vector<float> times;

    stft(input_flt,window_length,num_overlap,times,stft_out_);

    std::vector<std::vector<std::complex<float>>> stft_out = reverseindex_complex(stft_out_);

    std::vector<std::vector<float>> stft_mag;
    std::vector<std::vector<float>> stft_mag_sq;
    std::vector<std::vector<float>> B;

    stft_mag.resize(stft_out.size());
    stft_mag_sq.resize(stft_out.size());
    B.resize(stft_out.size());
    for (size_t i =0; i< stft_out.size(); i++){
        stft_mag[i].resize(stft_out[i].size());
        stft_mag_sq[i].resize(stft_out[i].size());
        B[i].resize(stft_out[i].size());
        for (size_t j=0; j< stft_out[i].size(); j++){
            stft_mag[i][j] = std::abs(stft_out[i][j]);
            stft_mag_sq[i][j] = stft_mag[i][j] * stft_mag[i][j];
            B[i][j] = 0;
        }
    }

    auto m = times.size();
    int n = window_length/2 +1;

    for (size_t i = 0; i < B.size(); i++){
        B[i] = autocorrelation(stft_mag_sq[i]);
    }

    std::vector<float> b(B[0].size());

    for (size_t i = 0; i < B.size(); i++){
        for (size_t j = 0 ; j<B[i].size();j++){
            b[j] += B[i][j];
        }
    }

    for (size_t i=0; i<b.size(); i++){
        b[i] = b[i]/n;
    }

    for (size_t i=0; i<b.size(); i++){
        b[i] = b[i]/b[0];
    }

    std::vector<float> b_valid(b.begin(),b.begin()+(size_t)(3*b.size()/4));
    auto l = b_valid.size();

    std::vector<float> J;
    J.resize(l/3);

    size_t delta1, delta2;
    float I, sum_;

    float h1,h2;

    for (size_t j = 1; j <(int)l/3+1; j++){
        if (j>=2){
            delta1 = 2;
        }
        else{
            delta1 =j;
        }
        delta2 = (float)(int)(3*j/4);
        I = 0;
        for (size_t i = j; i<l; i+=j){
            h1 = (float)findMaxIndex(b,(i-delta1),(i+delta1+1));
            h2 = (float)findMaxIndex(b,(i-delta2),(i+delta2+1));
            if (i-delta1 > 0){
                h1 += (i-delta1);
            }
            if (i-delta2 >0){
                h2 += (i-delta2);
            }
            sum_ = sumofVecotr(b,i-delta2,i+delta2+1);
            if (h1 == h2){
                I += b[(int)h1] - (float)(int)sum_/((2*delta2)+1);
            }
        }
        J[j-1] = I/(float)(int)l/j;
    }

    float p = (float)findMaxIndex(J,0,J.size()) + 1;

    int r = (int)stft_mag.size()/p;

    std::vector<std::vector<float>> S;
    S.resize(n);
    for (size_t i= 0; i<S.size(); i++){
        S[i].resize(p*r);
    }

    for (int i = 0; i < (int)n-1; i++) {
        for (int j = 0; j < (int)p; j++) {
            std::vector<float> values_at_l;
            for (int k = 0; k < (int)r; k++) {
                int index = j + k * p;
                if (index < stft_mag.size()) { // Ensure the index does not exceed column limits
                    values_at_l.push_back(stft_mag[i][index]);
                }
            }
            if (!values_at_l.empty()) {
                try {
                    S[i][l] = findMedian(values_at_l, 0, values_at_l.size() - 1);
                } catch (const std::invalid_argument& e) {
                    std::cerr << "Error: " << e.what() << std::endl;
                }
            }
        }
    }

    std::vector<std::vector<float>> W = stft_mag;
    size_t idx;
    for (size_t i = 0; i < n; i++){
        for (size_t j = 0; j<p; j++){
            for (size_t k = 0; k<r; k++){
                idx = j+k*p;
                if (idx < stft_mag.size()){
                    W[i][idx] = fmin(S[i][j],stft_mag[i][idx]);
                }
            }
        }
    }

    std::vector<std::vector<float>> M;
    M.resize(n);
    for (size_t i = 0; i<M.size(); i++){
        M[i].resize(m);
    }

    float temp;

    for (int i = 0; i<n-1;i++){
        for (int j=0; j< m-1; j++){
            temp = stft_mag[i][j];
            if (temp!=0){
                M[i][j] = W[i][j]/temp;
            }
            else{
                M[i][j] = 0;
            }
        }
    }

    std::vector<std::vector<std::complex<float>>> TempX;
    TempX.resize(stft_out.size());
    for (size_t i =0;i<stft_out.size();i++){
        TempX[i].resize(stft_out[i].size());
        for(size_t j = 0; j < stft_out[0].size();j++){
            TempX[i][j] = M[i][j] * stft_out[i][j];
        }
    }

    std::vector<std::vector<std::complex<float>>> TempX_ = reverseindex_complex(TempX);

    output1_flt = inverseSTFT(TempX,window_length,num_overlap,length);

    if (output1_flt.size() != length){
        output1_flt.resize(length);
    }

    for (size_t i = 0; i < output1_flt.size(); i++){
        output1[i] = (int)output1_flt[i];
        output2[i] = input[i] - (int)output1_flt[i];
    }

    return;
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


