# Whisper Transcriber

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

The Whisper Transcriber is an innovative desktop application designed to effortlessly convert audio and video content into accurate text transcripts. Leveraging the powerful OpenAI Whisper API for local processing, this tool offers a user-friendly graphical interface (GUI) built with PySide6 (Qt), making advanced transcription accessible to everyone.

### Why This Project Matters: A Real-World Problem Solved with AI

In today's fast-paced world, the need for efficient and accurate transcription is paramount, whether for content creation, accessibility, or information retrieval. Traditional transcription methods are often time-consuming, expensive, and prone to human error. This project addresses these challenges head-on by harnessing the power of Artificial Intelligence.

This application stands as a testament to how AI, specifically the Manus AI, can accelerate problem-solving in real-world scenarios. What might typically take weeks or months to develop was achieved significantly faster, demonstrating AI's potential for rapid prototyping and deployment without compromising efficiency. In fact, the scalability and cost-effectiveness achieved through this AI-assisted development are unparalleled.

### The Human Touch: Vision, Refinement, and Strategic Oversight

While AI played a pivotal role in the rapid development of the Whisper Transcriber, it's crucial to emphasize that this project's success is a direct result of human ingenuity and strategic oversight. My involvement was critical at every stage:

*   **Problem Identification:** Recognizing the core need for a streamlined, accessible transcription solution.
*   **Logical Structure & Design:** Architecting the 'what,' 'why,' and 'how' of the solution, laying down the foundational logic.
*   **Prompt Engineering & Refinement:** Guiding the AI with precise instructions and iteratively refining prompts to achieve desired outcomes.
*   **Code Review & Basic Refinement:** Ensuring code quality, functionality, and making necessary adjustments.
*   **Version Testing & Quality Assurance:** Rigorously testing different iterations to guarantee a robust and reliable application.

This project exemplifies a powerful synergy between human vision and AI capabilities, proving that when guided effectively, AI can amplify human potential, leading to groundbreaking solutions that are both efficient and economically viable.

## Table of Contents

*   [Features](#features)
*   [System Requirements](#system-requirements)
*   [Installation](#installation)
    *   [Python Installation](#1-python-installation)
    *   [Dependency Installation](#2-dependency-installation)
    *   [FFmpeg Installation](#3-ffmpeg-installation)
    *   [GPU Configuration (Optional)](#4-gpu-configuration-optional)
*   [Running the Application](#running-the-application)
*   [User Guide](#user-guide)
    *   [Main Interface](#main-interface)
    *   [Local Audio/Video Transcription](#local-audiovideo-transcription)
    *   [Batch Processing](#batch-processing)
    *   [Transcription Settings](#transcription-settings)
    *   [Text Export](#text-export)
*   [Troubleshooting](#troubleshooting)
    *   [Application does not start](#application-does-not-start)
    *   [Transcription error](#transcription-error)
    *   [Transcription is too slow](#transcription-is-too-slow)
    *   [CUDA out of memory error](#cuda-out-of-memory-error)
*   [Additional Information](#additional-information)
*   [Known Issues & Future Improvements](#known-issues--future-improvements)

## Features

*   **High-Accuracy Transcription:** Utilizes OpenAI's state-of-the-art Whisper API for superior transcription quality.
*   **Intuitive User Interface:** A sleek, dark-themed GUI built with PySide6 for an enhanced user experience.
*   **Local Processing:** Ensures data privacy and faster processing by performing transcription directly on your machine.
*   **Batch Processing:** Efficiently transcribe multiple audio/video files simultaneously.
*   **Customizable Settings:** Adjust language, model size, and processing device (CPU/GPU) to suit your needs.
*   **Direct Export:** Easily copy transcribed text or save it to a `.txt` file.

## System Requirements

*   **Operating System:** Windows 10 or higher (Linux/macOS compatibility may vary, but the core Python components are cross-platform).
*   **Python:** Version 3.8 or higher.
*   **Disk Space:** Minimum 2GB for installation (Whisper models can add up to 1.5GB).
*   **RAM:** Minimum 4GB (8GB or more recommended).
*   **NVIDIA GPU with CUDA support:** Optional, but highly recommended for significantly faster transcription.

## Installation

### 1. Python Installation

If you don't have Python installed:

1.  Visit [python.org](https://www.python.org/downloads/) and download the latest Python version for your OS.
2.  Run the installer and **ensure you check the option "`Add Python to PATH`" during installation.
3.  Follow the on-screen instructions to complete the installation.

### 2. Dependency Installation

The application requires several Python libraries. You can install them using the provided `install.py` script or manually via `pip`.

#### Using the Installation Script

1.  Open your Command Prompt or PowerShell (Windows) / Terminal (Linux/macOS).
2.  Navigate to the application folder: `cd path\to\whisper_transcriber`
3.  Execute the installation script: `python install.py`
4.  Wait for the installation to complete.

#### Manual Installation

If you prefer manual installation, run the following commands:

```bash
pip install PySide6
pip install openai-whisper
pip install torch
pip install torchvision
pip install torchaudio
```

### 3. FFmpeg Installation

FFmpeg is essential for audio and video processing:

1.  Download FFmpeg for your OS from [ffmpeg.org](https://ffmpeg.org/download.html) (choose the "static" version for Windows).
2.  Extract the contents of the ZIP file to a folder (e.g., `C:\ffmpeg` on Windows, `/usr/local/ffmpeg` on Linux/macOS).
3.  Add the `bin` folder to your system's PATH:
    *   **Windows:** Control Panel > System > Advanced system settings > Environment Variables > Edit "Path" and add the path (e.g., `C:\ffmpeg\bin`).
    *   **Linux/macOS:** Add `export PATH="/path/to/ffmpeg/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc` file and then run `source ~/.bashrc` (or `~/.zshrc`).

### 4. GPU Configuration (Optional)

To leverage your GPU for accelerated transcription:

1.  Install the latest NVIDIA drivers.
2.  Install the CUDA Toolkit compatible with your PyTorch version:
    *   Visit [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads).
    *   Download and install the recommended version.

## Running the Application

1.  Open your Command Prompt or PowerShell (Windows) / Terminal (Linux/macOS).
2.  Navigate to the application folder: `cd path\to\whisper_transcriber`
3.  Execute the application: `python main.py`

## User Guide

### Main Interface

The application is organized into several intuitive sections:

*   **Media Input**: For selecting local files or folders.
*   **Settings**: To adjust language, model, and processing device.
*   **Batch Processing**: To manage multiple files for transcription.
*   **Text Viewer**: To view and export the transcribed text.

### Local Audio/Video Transcription

1.  In the "Media Input" tab, click "Browse File."
2.  Select your desired audio or video file.
3.  Click "Transcribe" to start the transcription.
4.  Wait for the process to complete.
5.  The transcribed text will be displayed in the viewer and automatically saved as a `.txt` file in the same location as the original media file.

### Batch Processing

1.  Add files to the batch list:
    *   In the "Media Input" tab, select a file and click "Add to Batch."
    *   Alternatively, click "Browse Folder" to add all media files from a selected folder.
2.  In the "Batch Processing" tab, you will see all added items.
3.  Click "Process All" to begin batch processing.
4.  Transcriptions will be automatically saved in the source folder of the files, each named after the original file.

### Transcription Settings

In the "Settings" tab, you can fine-tune:

*   **Language**: Select the audio language or use automatic detection.
*   **Model**: Choose from different model sizes:

| Option | Description | Speed | Accuracy |
|---|---|---|---|
| Tiny | Fastest, lower accuracy | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Base | Balance of speed and accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Small | Good accuracy with reasonable performance | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Medium | High accuracy, slower | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Large | Maximum accuracy, slower | ⭐ | ⭐⭐⭐⭐⭐⭐ |

*   **Device**: Select between CPU or GPU (CUDA) for processing.

### Text Export

After transcription:

1.  The transcribed text is displayed in the viewer.
2.  Click "Copy to Clipboard" to copy the text.
3.  Click "Save as TXT" to save the text to a file.
4.  Choose the location and filename in the dialog box.

## Troubleshooting

### Application does not start

*   Verify Python is installed correctly.
*   Ensure all dependencies are installed.
*   Run the application from the Command Prompt/Terminal to check for error messages.

### Transcription error

*   Verify the Whisper model downloaded correctly.
*   For large files, try using a smaller model (tiny or base).
*   If using GPU, ensure CUDA is configured correctly.

### Transcription is too slow

*   Use a smaller model (tiny or base) for faster speed.
*   Enable GPU processing in settings.
*   Verify your GPU is CUDA compatible.

### "CUDA out of memory" error

*   Choose a smaller model in settings.
*   Close other applications that might be using the GPU.
*   Try using the CPU for processing.

## Additional Information

*   Whisper models are downloaded automatically upon first execution.
*   Model downloads may take a few minutes depending on your internet connection.
*   Batch transcriptions are automatically saved in the same folder as the original files.

## Known Issues & Future Improvements

This project is actively under development. While functional, you might encounter:

*   **Minor Bugs:** Some edge cases or unexpected behaviors may still exist.
*   **UI/UX Enhancements:** The user interface is currently basic and will be improved in future iterations to offer a more polished and intuitive experience.

We are committed to continuous improvement and will address these areas in upcoming updates.

