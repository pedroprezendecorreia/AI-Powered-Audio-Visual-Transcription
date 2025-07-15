"""
Batch processing module for the transcription application.
"""
import os
import threading
from queue import Queue
from pathlib import Path
from PySide6.QtCore import QObject, Signal

class BatchProcessorSignals(QObject):
    """
    Signals for communication with the interface during batch processing.
    """
    item_completed = Signal(int, str, str)  # index, path, text
    batch_progress = Signal(int, str)  # percentage, message
    item_progress = Signal(int, int, str)  # index, percentage, message
    batch_completed = Signal(dict)  # results
    error_occurred = Signal(str)  # error message
    confirmation_needed = Signal(int, str, str)  # index, path, text

class BatchProcessor:
    """
    Class for managing batch processing.
    """
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.batch_thread = None
        self.is_processing = False
        self.cancel_requested = False
        self.pause_requested = False
        self.current_item_index = -1
        self.items_queue = Queue()
        self.results = {}
        self.signals = BatchProcessorSignals()
        self.waiting_confirmation = False
    
    def process_batch(self, items, config):
        """
        Starts batch processing.
        
        Args:
            items (list): List of items (file paths)
            config (dict): Transcription settings
        """
        if self.is_processing:
            self.signals.error_occurred.emit("A batch process is already in progress.")
            return
        
        self.is_processing = True
        self.cancel_requested = False
        self.pause_requested = False
        self.current_item_index = -1
        self.results = {}
        self.waiting_confirmation = False
        
        # Clear and populate the queue
        while not self.items_queue.empty():
            self.items_queue.get()
        
        for item in items:
            self.items_queue.put(item)
        
        # Start batch processing thread
        self.batch_thread = threading.Thread(
            target=self._batch_thread,
            args=(items, config)
        )
        self.batch_thread.daemon = True
        self.batch_thread.start()
    
    def _batch_thread(self, items, config):
        """
        Batch processing thread.
        
        Args:
            items (list): List of items (file paths)
            config (dict): Transcription settings
        """
        try:
            total_items = len(items)
            processed_items = 0
            
            while not self.items_queue.empty() and not self.cancel_requested:
                # Get next item
                item = self.items_queue.get()
                self.current_item_index += 1
                
                # Update batch progress
                batch_progress = int((processed_items / total_items) * 100)
                self.signals.batch_progress.emit(
                    batch_progress, 
                    f"Processing item {processed_items + 1} of {total_items}: {os.path.basename(item)}"
                )
                
                # Process media file
                self._process_media_file(item, config)
                
                # Wait for confirmation before proceeding
                self.waiting_confirmation = True
                while self.waiting_confirmation and not self.cancel_requested:
                    # Wait for user confirmation
                    threading.Event().wait(0.1)
                
                processed_items += 1
                
                # Check for cancellation after each item
                if self.cancel_requested:
                    break
            
            # Finalize batch processing
            if not self.cancel_requested:
                self.signals.batch_completed.emit(self.results)
        
        except Exception as e:
            self.signals.error_occurred.emit(f"Error in batch processing: {str(e)}")
        
        finally:
            self.is_processing = False
    
    def _process_media_file(self, file_path, config):
        """
        Processes a media file.
        
        Args:
            file_path (str): Path to the media file
            config (dict): Transcription settings
        """
        if not os.path.isfile(file_path):
            self.signals.error_occurred.emit(f"File not found: {file_path}")
            return
        
        self.signals.item_progress.emit(self.current_item_index, 0, "Starting transcription...")
        
        # Configure callbacks for transcription
        def transcribe_progress(percent, status=None):
            self.signals.item_progress.emit(
                self.current_item_index, 
                percent, 
                status or f"Transcription: {percent}%"
            )
        
        def transcribe_complete(text):
            self.signals.item_progress.emit(self.current_item_index, 100, "Transcription completed")
            
            # Store result
            self.results[file_path] = text
            
            # Request user confirmation
            self.signals.confirmation_needed.emit(self.current_item_index, file_path, text)
        
        def transcribe_error(error_msg):
            self.signals.error_occurred.emit(error_msg)
            # Proceed to the next item
            self.waiting_confirmation = False
        
        # Start transcription
        self.transcriber.transcribe(
            file_path,
            config,
            progress_callback=transcribe_progress,
            completion_callback=transcribe_complete,
            error_callback=transcribe_error
        )
    
    def confirm_and_continue(self, save=True, file_path=None, text=None):
        """
        Confirms processing of the current item and continues to the next.
        
        Args:
            save (bool): If True, saves the text file
            file_path (str): Path to the processed file
            text (str): Transcribed text
        """
        if save and file_path and text:
            try:
                # Determine directory and file name
                output_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.txt")
                
                # Save the file
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                # Notify item completion
                self.signals.item_completed.emit(self.current_item_index, file_path, output_path)
            except Exception as e:
                self.signals.error_occurred.emit(f"Error saving file: {str(e)}")
        
        # Continue to the next item
        self.waiting_confirmation = False
    
    def cancel(self):
        """
        Cancels batch processing.
        
        Returns:
            bool: True if cancellation was initiated, False otherwise
        """
        if self.is_processing:
            self.cancel_requested = True
            self.waiting_confirmation = False
            
            # Cancel ongoing operations
            if self.transcriber.is_transcribing:
                self.transcriber.cancel()
            
            return True
        
        return False
    
    def cancel_item(self, index):
        """
        Cancels a specific item in the batch.
        
        Args:
            index (int): Index of the item to be canceled
            
        Returns:
            bool: True if cancellation was initiated, False otherwise
        """
        if self.is_processing and index == self.current_item_index:
            # Cancel current operation
            if self.transcriber.is_transcribing:
                self.transcriber.cancel()
            
            # Proceed to the next item
            self.waiting_confirmation = False
            
            return True
        
        return False


