"""
Progress bar and status component for the transcription application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class ProgressBar(QWidget):
    """
    Widget to display progress and status of operations.
    """
    # Signals
    cancel_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main progress bar
        self.progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_layout.addWidget(self.progress_bar, 1)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setEnabled(False)
        self.progress_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(self.progress_layout)
        
        # Main status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setBold(True)
        self.status_label.setFont(font)
        self.layout.addWidget(self.status_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
        # Detailed status
        self.detailed_status_label = QLabel("")
        self.detailed_status_label.setAlignment(Qt.AlignLeft)
        self.detailed_status_label.setWordWrap(True)
        self.layout.addWidget(self.detailed_status_label)
        
        # Activity indicator
        self.activity_indicator = QLabel("⏳")
        self.activity_indicator.setAlignment(Qt.AlignRight)
        self.activity_indicator.setVisible(False)
        self.layout.addWidget(self.activity_indicator)
        
        # Timer for activity indicator animation
        self.animation_counter = 0
        self.animation_symbols = ["⏳", "⌛", "⏳", "⌛"]
    
    def set_progress(self, value, detailed_status=None):
        """
        Sets the progress bar value.
        
        Args:
            value (int): Progress value (0-100)
            detailed_status (str, optional): Detailed status
        """
        self.progress_bar.setValue(value)
        
        if detailed_status:
            self.detailed_status_label.setText(detailed_status)
            
        # Update activity indicator
        if value > 0 and value < 100:
            self.activity_indicator.setVisible(True)
            self.animation_counter = (self.animation_counter + 1) % len(self.animation_symbols)
            self.activity_indicator.setText(self.animation_symbols[self.animation_counter])
        else:
            self.activity_indicator.setVisible(False)
    
    def set_status(self, text):
        """
        Sets the status text.
        
        Args:
            text (str): Status text
        """
        self.status_label.setText(text)
    
    def start_operation(self):
        """
        Starts an operation, enabling the cancel button.
        """
        self.cancel_button.setEnabled(True)
        self.activity_indicator.setVisible(True)
    
    def finish_operation(self):
        """
        Finishes an operation, disabling the cancel button.
        """
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.detailed_status_label.setText("")
        self.activity_indicator.setVisible(False)
    
    def on_cancel_clicked(self):
        """
        Handler for the cancel button click.
        """
        self.cancel_requested.emit()


