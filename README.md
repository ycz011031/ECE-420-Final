# Audio Signal Processing Project

## Overview
This project focuses on advanced audio signal processing techniques, including:
- **Music and Voice Separation**: Extracting distinct components from audio files.
- **Epoch Location Detection**: Identifying key points in audio signals for further analysis.
- **Audio File Manipulation**: Reading, processing, and writing `.wav` files.

The project is implemented in C++ for the Android application, with a Python prototype for testing and development.

## Features
1. **Android Application (C++)**:
   - Core algorithms for audio processing are implemented in C++.
   - Key files:
     - `ece420_lib.cpp`: Utility functions for audio processing.
     - `ece420_main.cpp`: Main logic for pitch shifting and epoch detection.
     - `Repet.cpp`: Advanced audio processing techniques.

2. **Python Prototype**:
   - `imports.py`: Essential library imports for audio processing.
   - `Library.py`: Core functions for epoch detection and audio manipulation.
   - `Main.py`: Main script for orchestrating the audio processing pipeline.

3. **Test Data**:
   - `test_audio/`: Contains sample `.wav` files for testing.
   - `test_output/`: Stores processed audio outputs.

## How to Run
### Android Application
1. Open the `Android_Build` folder in Android Studio.
2. Build and run the application on an emulator or physical device.

### Python Prototype
1. Navigate to the `Python Build` directory.
2. Run `Main.py` to execute the audio processing pipeline.

## Project Structure
```
ECE-420-Final/
├── Python Build/
│   ├── imports.py
│   ├── Library.py
│   ├── Main.py
│   ├── test_audio/
│   └── test_output/
├── Android_Build/
│   ├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── cpp/
│   │   │   │   ├── ece420_lib.cpp
│   │   │   │   ├── ece420_main.cpp
│   │   │   │   ├── Repet.cpp
│   └── build.gradle
├── Documents/
│   ├── Final_report/
│   └── Initial_proposal/
└── README.md
```

## Contributors
- Y. Zhou
- L. Tang
