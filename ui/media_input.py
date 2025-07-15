"""
Media input component for the transcription application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt, Signal

class MediaInput(QWidget):
    """
    Widget for media input (local file).
    """
    # Signals
    file_selected = Signal(str)
    folder_selected = Signal(str)
    add_to_batch = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Local file input section
        self.setup_file_section()
    
    def setup_file_section(self):
        """
        Sets up the local file selection section.
        """
        file_group = QGroupBox("Local File")
        file_layout = QVBoxLayout(file_group)
        
        # Description
        file_desc = QLabel("Select an audio or video file from your computer:")
        file_layout.addWidget(file_desc)
        
        # Input field and button
        file_input_layout = QHBoxLayout()
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("File path...")
        self.file_path_input.setReadOnly(True)
        file_input_layout.addWidget(self.file_path_input, 1)
        
        self.browse_button = QPushButton("Browse File")
        self.browse_button.clicked.connect(self.on_browse_clicked)
        file_input_layout.addWidget(self.browse_button)
        
        self.browse_folder_button = QPushButton("Browse Folder")
        self.browse_folder_button.clicked.connect(self.on_browse_folder_clicked)
        file_input_layout.addWidget(self.browse_folder_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        file_input_layout.addWidget(self.clear_button)
        
        file_layout.addLayout(file_input_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.transcribe_button = QPushButton("Transcribe")
        self.transcribe_button.clicked.connect(self.on_transcribe_clicked)
        action_layout.addWidget(self.transcribe_button)
        
        self.add_to_batch_file_button = QPushButton("Add to Batch")
        self.add_to_batch_file_button.clicked.connect(self.on_add_to_batch_file_clicked)
        action_layout.addWidget(self.add_to_batch_file_button)
        
        file_layout.addLayout(action_layout)
        
        # Add to main layout
        self.layout.addWidget(file_group)
        
        # Add spacer to push everything up
        self.layout.addStretch()
    
    def on_browse_clicked(self):
        """
        Handler for the browse file button click.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio/Video File",
            "",
            "Media Files (*.mp3 *.mp4 *.wav *.ogg *.flac *.avi *.mov *.mkv *.webm);;All Files (*)"
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
            self.file_selected.emit(file_path)
    
    def on_browse_folder_clicked(self):
        """
        Handler for the browse folder button click.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Audio/Video Files",
            ""
        )
        
        if folder_path:
            self.file_path_input.setText(folder_path)
            self.folder_selected.emit(folder_path)
    
    def on_clear_clicked(self):
        """
        Handler for the clear button click.
        """
        self.file_path_input.clear()
    
    def on_transcribe_clicked(self):
        """
        Handler for the transcribe button click.
        """
        file_path = self.file_path_input.text()
        if file_path:
            self.file_selected.emit(file_path)
    
    def on_add_to_batch_file_clicked(self):
        """
        Handler for the add file to batch button click.
        """
        file_path = self.file_path_input.text()
        if file_path:
            self.add_to_batch.emit(file_path)


