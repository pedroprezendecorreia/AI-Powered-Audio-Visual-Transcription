"""
Transcription module using OpenAI's Whisper API.
"""
import os
import torch
import whisper
import threading
import time
from pathlib import Path

class Transcriber:
    """
    Class for audio transcription using OpenAI's Whisper API.
    """
    def __init__(self):
        self.transcription_thread = None
        self.is_transcribing = False
        self.model = None
        self.current_model_name = None
        self.cancel_requested = False
        self.start_time = 0
        self.estimated_total_time = 0
    
    def transcribe(self, file_path, config, progress_callback=None, completion_callback=None, error_callback=None):
        """
        Starts transcription of an audio file.
        
        Args:
            file_path (str): Path to the audio file
            config (dict): Transcription settings (language, model, device)
            progress_callback (callable): Callback function for progress updates
            completion_callback (callable): Callback function for transcription completion
            error_callback (callable): Callback function for errors
        """
        if self.is_transcribing:
            if error_callback:
                error_callback("A transcription is already in progress.")
            return
        
        self.is_transcribing = True
        self.cancel_requested = False
        self.start_time = time.time()
        self.estimated_total_time = 0
        
        # Start transcription thread
        self.transcription_thread = threading.Thread(
            target=self._transcribe_thread,
            args=(file_path, config, progress_callback, completion_callback, error_callback)
        )
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def _transcribe_thread(self, file_path, config, progress_callback, completion_callback, error_callback):
        """
        Transcription thread.
        
        Args:
            file_path (str): Path to the audio file
            config (dict): Transcription settings (language, model, device)
            progress_callback (callable): Callback function for progress updates
            completion_callback (callable): Callback function for transcription completion
            error_callback (callable): Callback function for errors
        """
        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                if error_callback:
                    error_callback(f"File not found: {file_path}")
                return
            
            # Extract settings
            model_name = config.get("model", "base")
            language = config.get("language", "auto")
            device = config.get("device", "cuda" if torch.cuda.is_available() else "cpu")
            
            # Check GPU availability
            if device == "cuda" and not torch.cuda.is_available():
                if progress_callback:
                    progress_callback(0, "GPU not available, using CPU")
                device = "cpu"
            
            # Load model if necessary
            if progress_callback:
                progress_callback(10, f"Loading model {model_name}...")
            
            # Load new model only if it's different from the current one
            if self.model is None or self.current_model_name != model_name:
                self.model = whisper.load_model(model_name, device=device)
                self.current_model_name = model_name
            
            if self.cancel_requested:
                return
            
            # Configure transcription options
            transcribe_options = {}
            
            # Set language if not auto
            if language != "auto":
                transcribe_options["language"] = language
            
            # Configure fp16 based on device
            transcribe_options["fp16"] = (device == "cuda")
            
            # Estimate total time based on file size and model
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Time estimation factors per model (seconds per MB)
            time_factors = {
                "tiny": 1.0,
                "base": 2.0,
                "small": 4.0,
                "medium": 8.0,
                "large": 16.0
            }
            
            # Adjust factor based on device
            device_factor = 1.0 if device == "cuda" else 3.0
            
            # Calculate time estimate
            self.estimated_total_time = file_size_mb * time_factors.get(model_name, 2.0) * device_factor
            
            if progress_callback:
                elapsed_time = time.time() - self.start_time
                remaining_time = max(0, self.estimated_total_time - elapsed_time)
                progress_callback(30, f"Starting transcription... Estimated time: {format_time(self.estimated_total_time)}")
            
            # Perform transcription
            result = self.model.transcribe(file_path, **transcribe_options)
            
            if self.cancel_requested:
                return
            
            if progress_callback:
                elapsed_time = time.time() - self.start_time
                progress_callback(90, f"Finalizing transcription... Elapsed time: {format_time(elapsed_time)}")
            
            # Extract text
            transcribed_text = result.get("text", "")
            
            # Calculate total time
            total_time = time.time() - self.start_time
            
            if completion_callback:
                completion_callback(transcribed_text)
        
        except Exception as e:
            if error_callback:
                error_callback(f"Transcription error: {str(e)}")
        
        finally:
            self.is_transcribing = False
    
    def cancel(self):
        """
        Cancels the ongoing transcription.
        """
        if self.is_transcribing:
            self.cancel_requested = True
            return True
        return False

def format_time(seconds):
    """
    Formats time in seconds to a readable string.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}min {seconds}s"
    elif minutes > 0:
        return f"{minutes}min {seconds}s"
    else:
        return f"{seconds}s"


