# Application Architecture: Whisper Transcriber

## Overview

The Whisper Transcriber application is built upon a modular architecture, ensuring a clear separation between the graphical user interface (frontend) and the core processing logic (backend). This design choice is crucial for maintaining a responsive user interface during lengthy processing operations and significantly simplifies future maintenance and expansion of the codebase.

## Directory Structure

```
whisper_transcriber/
├── main.py                  # Application entry point
├── install.py               # Installation script
├── requirements.txt         # Project dependencies (to be created)
├── README.md                # Main documentation
├── ARCHITECTURE.md          # Detailed architecture documentation
├── todo.md                  # Project tasks and roadmap
├── ui/                      # User Interface modules
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── media_input.py       # Media input component
│   ├── batch_list.py        # Batch processing list component
│   ├── transcription_config.py # Transcription settings component
│   ├── progress_bar.py      # Progress bar component
│   ├── text_viewer.py       # Transcribed text viewer component
│   └── resources/           # UI resources (icons, styles)
│       └── style.qss        # Dark theme stylesheet
└── core/                    # Core processing modules
    ├── __init__.py
    ├── youtube_downloader.py # YouTube video download functionality
    ├── transcriber.py       # Whisper API integration for transcription
    ├── batch_processor.py   # Batch processing and multithreading management
    └── file_manager.py      # File operations management
```

## Key Modules

### User Interface (UI)

1.  **MainWindow**: The central window that integrates all UI components, managing the overall application flow and state.
2.  **MediaInput**: Handles user input for media, supporting both local file selection and YouTube URL processing.
3.  **BatchList**: Manages the queue of files designated for batch transcription, providing controls for adding, removing, and monitoring items.
4.  **TranscriptionConfig**: Allows users to configure transcription parameters such as language, Whisper model size, and the processing device (CPU/GPU).
5.  **ProgressBar**: Displays the real-time progress and status of ongoing operations, providing visual feedback to the user.
6.  **TextView**: Facilitates the viewing and exporting of transcribed text, offering options to copy to clipboard or save as a `.txt` file.

### Core (Backend)

1.  **YouTubeDownloader**: Responsible for downloading videos from YouTube using `yt-dlp`, ensuring media is ready for transcription.
2.  **Transcriber**: Integrates with the OpenAI Whisper API, handling the core logic for audio-to-text conversion.
3.  **BatchProcessor**: Manages the efficient processing of multiple transcription tasks, leveraging multithreading to optimize performance.
4.  **FileManager**: Provides utilities for various file operations, including reading, writing, and exporting transcribed content.

## Data Flow

**Media Input** → **Processing** → **Viewing/Exporting**

*   **Input**: YouTube URL or local audio/video file.
*   **Processing**: Involves media download (if from YouTube) and the transcription process via the Whisper API.
*   **Output**: Transcribed text, available for immediate viewing within the application and for export to various formats.

## Multithreading System

To ensure a smooth and responsive user experience, the application employs a robust multithreading system:

*   **WorkerThread**: Dedicated threads are utilized for long-running operations, such as media downloading and transcription, preventing the UI from freezing.
*   **SignalBus**: A signal-based communication mechanism (leveraging Qt's signals and slots) facilitates asynchronous communication between threads, ensuring data consistency and responsiveness.
*   **ProgressUpdater**: A specialized mechanism for updating the UI with real-time progress of operations, keeping the user informed.

## Inter-Module Communication

*   **Qt Signals and Slots**: Asynchronous communication between UI and backend modules is primarily handled through Qt's signal and slot mechanism, promoting loose coupling and modularity.
*   **Events**: Custom events are used to notify modules about the completion of operations, progress updates, and error occurrences.
*   **Callbacks**: Callbacks are employed for specific state updates and to provide immediate visual feedback to the user.

## State Management

*   The overall application state is centrally managed by the `MainWindow`, ensuring consistency across different components.
*   Individual component states are encapsulated within their respective classes, promoting reusability and maintainability.
*   An interface locking/unlocking system is implemented to prevent user interaction during critical, long-running operations.

## Error Handling

*   A centralized exception handling system is in place to gracefully manage errors and prevent application crashes.
*   Users receive clear visual feedback in case of errors, guiding them towards potential solutions.
*   Detailed logs are generated to assist with debugging and troubleshooting.

## Performance Considerations

*   The application is designed for efficient resource utilization during transcription, especially for large files.
*   Optimizations are in place to ensure optimal performance across various hardware configurations.
*   Automatic detection of GPU availability allows the application to leverage hardware acceleration when possible.
*   Dynamic configuration adjustments are made based on the detected hardware capabilities to maximize efficiency.


