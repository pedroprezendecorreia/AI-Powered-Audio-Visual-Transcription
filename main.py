"""
Main application file for the transcription app.
"""
import sys
import os
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool

from ui.main_window import MainWindow
from ui.media_input import MediaInput
from ui.batch_list import BatchList
from ui.transcription_config import TranscriptionConfig
from ui.progress_bar import ProgressBar
from ui.text_viewer import TextView

from core.transcriber import Transcriber
from core.batch_processor import BatchProcessor
from core.file_manager import FileManager

class ApplicationController(QObject):
    """
    Main application controller, managing communication between UI and backend.
    """
    # Signals for UI updates
    update_progress = Signal(int, str)
    update_status = Signal(str)
    update_text_view = Signal(str)
    processing_started = Signal()
    processing_finished = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Initialize backend components
        self.transcriber = Transcriber()
        self.batch_processor = BatchProcessor(self.transcriber)
        self.file_manager = FileManager()
        
        # Current configuration
        self.current_config = {
            'language': 'auto',
            'model': 'base',
            'device': 'cuda'
        }
        
        # Thread pool for background operations
        self.thread_pool = QThreadPool()
        
        # Connect batch processor signals
        self.batch_processor.signals.item_progress.connect(self.on_batch_item_progress)
        self.batch_processor.signals.batch_progress.connect(self.on_batch_progress)
        self.batch_processor.signals.item_completed.connect(self.on_batch_item_completed)
        self.batch_processor.signals.batch_completed.connect(self.on_batch_completed)
        self.batch_processor.signals.error_occurred.connect(self.on_batch_error)
        self.batch_processor.signals.confirmation_needed.connect(self.on_confirmation_needed)
    
    def setup_main_window(self, main_window):
        """
        Sets up the main window and connects signals and slots.
        
        Args:
            main_window (MainWindow): The main application window
        """
        self.main_window = main_window
        
        # Initialize UI components
        self.setup_media_input()
        self.setup_batch_list()
        self.setup_transcription_config()
        self.setup_progress_bar()
        self.setup_text_viewer()
        
        # Connect global signals
        self.update_progress.connect(self.progress_bar.set_progress)
        self.update_status.connect(self.main_window.status_bar.showMessage)
        self.update_text_view.connect(self.text_viewer.set_text)
        self.processing_started.connect(self.progress_bar.start_operation)
        self.processing_finished.connect(self.progress_bar.finish_operation)
    
    def setup_media_input(self):
        """
        Sets up the media input component.
        """
        self.media_input = MediaInput()
        self.main_window.media_input_layout.addWidget(self.media_input)
        
        # Connect signals
        self.media_input.file_selected.connect(self.transcribe_file)
        self.media_input.folder_selected.connect(self.add_folder_to_batch)
        self.media_input.add_to_batch.connect(self.add_to_batch)
    
    def setup_batch_list(self):
        """
        Sets up the batch list component.
        """
        self.batch_list = BatchList()
        self.main_window.batch_layout.addWidget(self.batch_list)
        
        # Connect signals
        self.batch_list.batch_process_requested.connect(self.process_batch)
        self.batch_list.folder_selected.connect(self.add_folder_to_batch)
    
    def setup_transcription_config(self):
        """
        Sets up the transcription configuration component.
        """
        self.transcription_config = TranscriptionConfig()
        self.main_window.config_layout.addWidget(self.transcription_config)
        
        # Connect signals
        self.transcription_config.config_changed.connect(self.update_config)
    
    def setup_progress_bar(self):
        """
        Sets up the progress bar component.
        """
        self.progress_bar = ProgressBar()
        self.main_window.main_layout.addWidget(self.progress_bar)
        
        # Connect signals
        self.progress_bar.cancel_requested.connect(self.cancel_operation)
    
    def setup_text_viewer(self):
        """
        Sets up the text viewer component.
        """
        self.text_viewer = TextView()
        self.main_window.bottom_layout.addWidget(self.text_viewer)
        
        # Remove placeholder
        if hasattr(self.main_window, 'text_view_placeholder'):
            self.main_window.text_view_placeholder.setParent(None)
            self.main_window.text_view_placeholder = None
    
    @Slot(dict)
    def update_config(self, config):
        """
        Updates the current configuration.
        
        Args:
            config (dict): New configuration
        """
        self.current_config = config
    
    @Slot(str)
    def transcribe_file(self, file_path):
        """
        Starts transcription of a file.
        
        Args:
            file_path (str): File path
        """
        if not file_path:
            return
        
        if not os.path.isfile(file_path):
            self.update_status.emit(f"File not found: {file_path}")
            return
        
        self.processing_started.emit()
        self.update_status.emit(f"Starting transcription: {file_path}")
        
        # Configure callbacks
        def progress_callback(percent, status=None):
            self.update_progress.emit(percent, status or f"Transcription: {percent}%")
        
        def completion_callback(text):
            self.update_status.emit("Transcription completed")
            self.update_text_view.emit(text)
            
            # Automatically save the text file
            try:
                output_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.txt")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                self.update_status.emit(f"Transcription saved to: {output_path}")
            except Exception as e:
                self.update_status.emit(f"Error saving transcription: {str(e)}")
            
            self.processing_finished.emit()
        
        def error_callback(error_msg):
            self.update_status.emit(f"Error: {error_msg}")
            self.processing_finished.emit()
        
        # Start transcription
        self.transcriber.transcribe(
            file_path,
            self.current_config,
            progress_callback=progress_callback,
            completion_callback=completion_callback,
            error_callback=error_callback
        )
    
    @Slot(str)
    def add_folder_to_batch(self, folder_path):
        """
        Adds all media files from a folder to the batch.
        
        Args:
            folder_path (str): Folder path
        """
        if not folder_path or not os.path.isdir(folder_path):
            self.update_status.emit("Invalid folder")
            return
        
        # Find all media files in the folder
        media_files = self.file_manager.find_media_files_in_folder(folder_path)
        
        # Add files to batch
        if media_files:
            for file_path in media_files:
                self.batch_list.add_item(file_path)
            
            self.update_status.emit(f"Added {len(media_files)} files to batch")
        else:
            self.update_status.emit("No media files found in folder")
    
    @Slot(str)
    def add_to_batch(self, item):
        """
        Adds an item to the batch list.
        
        Args:
            item (str): Item to be added (file path)
        """
        if not item:
            return
        
        # Check if it's a local file
        is_file = os.path.isfile(item)
        
        if not is_file:
            self.update_status.emit("Invalid item for batch processing")
            return
        
        # Add to list
        self.batch_list.add_item(item)
        self.update_status.emit(f"Item added to batch: {item}")
    
    @Slot(list)
    def process_batch(self, items):
        """
        Starts batch processing.
        
        Args:
            items (list): List of items to be processed
        """
        if not items:
            return
        
        self.processing_started.emit()
        self.update_status.emit(f"Starting batch processing: {len(items)} items")
        
        # Start batch processing
        self.batch_processor.process_batch(items, self.current_config)
    
    @Slot(int, int, str)
    def on_batch_item_progress(self, index, percent, status):
        """
        Handler for individual batch item progress.
        
        Args:
            index (int): Item index
            percent (int): Progress percentage
            status (str): Status message
        """
        self.update_progress.emit(percent, f"Item {index + 1}: {status}")
    
    @Slot(int, str)
    def on_batch_progress(self, percent, status):
        """
        Handler for overall batch progress.
        
        Args:
            percent (int): Progress percentage
            status (str): Status message
        """
        self.update_status.emit(status)
    
    @Slot(int, str, str)
    def on_batch_item_completed(self, index, file_path, output_path):
        """
        Handler for individual batch item completion.
        
        Args:
            index (int): Item index
            file_path (str): Processed file path
            output_path (str): Output file path
        """
        file_name = os.path.basename(file_path)
        self.update_status.emit(f"Transcription saved to: {output_path}")
        
        # Clear the viewer area
        self.update_text_view.emit("")
        
        # Notify that it's proceeding to the next item
        if self.batch_processor.current_item_index < len(self.batch_list.get_all_items()) - 1:
            next_file = self.batch_list.get_all_items()[self.batch_processor.current_item_index + 1]
            next_file_name = os.path.basename(next_file)
            self.update_status.emit(f"Proceeding to next item: {next_file_name}")
    
    @Slot(dict)
    def on_batch_completed(self, results):
        """
        Handler for batch completion.
        
        Args:
            results (dict): Batch processing results
        """
        self.update_status.emit(f"Batch processing completed: {len(results)} items")
        self.processing_finished.emit()
    
    @Slot(str)
    def on_batch_error(self, error_msg):
        """
        Handler for errors in batch processing.
        
        Args:
            error_msg (str): Error message
        """
        self.update_status.emit(f"Error: {error_msg}")
    
    @Slot(int, str, str)
    def on_confirmation_needed(self, index, file_path, text):
        """
        Handler for confirmation request.
        
        Args:
            index (int): Item index
            file_path (str): Processed file path
            text (str): Transcribed text
        """
        # Show the transcribed text
        self.update_text_view.emit(text)
        
        # Show confirmation dialog
        file_name = os.path.basename(file_path)
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("Transcription Confirmation")
        msg_box.setText(f"Transcription for file '{file_name}' completed.")
        msg_box.setInformativeText("Do you want to save this transcription and continue to the next item?")
        
        # Buttons in English
        btn_save_continue = msg_box.addButton("Save and Continue", QMessageBox.YesRole)
        btn_save_stop = msg_box.addButton("Save and Stop", QMessageBox.NoRole)
        btn_cancel = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(btn_save_continue)
        
        # Add file details
        details = f"File: {file_path}\n"
        details += f"Transcription size: {len(text)} characters\n"
        details += f"First 100 characters: {text[:100]}..."
        msg_box.setDetailedText(details)
        
        # Execute dialog
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == btn_save_continue:
            # Save and continue
            self.batch_processor.confirm_and_continue(True, file_path, text)
        elif clicked_button == btn_save_stop:
            # Save and stop processing
            self.batch_processor.confirm_and_continue(True, file_path, text)
            # Cancel batch processing after saving current item
            self.cancel_operation()
        else:  # btn_cancel
            # Cancel batch processing
            self.cancel_operation()
    
    @Slot()
    def cancel_operation(self):
        """
        Cancels the ongoing operation.
        """
        # Try to cancel ongoing operations
        if self.transcriber.is_transcribing:
            self.transcriber.cancel()
            self.update_status.emit("Transcription canceled")
        
        if self.batch_processor.is_processing:
            self.batch_processor.cancel()
            self.update_status.emit("Batch processing canceled")
        
        self.processing_finished.emit()

def main():
    """
    Main function of the application.
    """
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = MainWindow()
    
    # Create controller
    controller = ApplicationController()
    controller.setup_main_window(main_window)
    
    # Show window
    main_window.show()
    
    # Execute event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


