"""
Main interface component for the transcription application.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QSplitter, QLabel, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

class MainWindow(QMainWindow):
    """
    Main window of the transcription application.
    """
    def __init__(self):
        super().__init__()
        
        # Main window configuration
        self.setWindowTitle("Whisper Transcriber")
        self.setMinimumSize(900, 600)
        
        # Load stylesheet
        self._load_stylesheet()
        
        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Create interface components
        self._setup_ui()
        
        # Configure status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _load_stylesheet(self):
        """
        Loads the dark blue theme stylesheet.
        """
        try:
            with open("ui/resources/style.qss", "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
    
    def _setup_ui(self):
        """
        Sets up the user interface components.
        """
        # Application title
        title_label = QLabel("Whisper Transcriber")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.main_layout.addWidget(title_label)
        
        # Main splitter
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.main_splitter)
        
        # Top panel (input and settings)
        self.top_panel = QWidget()
        self.top_layout = QVBoxLayout(self.top_panel)
        
        # Tabs for media input and settings
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Media input tab
        self.media_input_tab = QWidget()
        self.media_input_layout = QVBoxLayout(self.media_input_tab)
        self.tabs.addTab(self.media_input_tab, "Media Input")
        
        # Settings tab
        self.config_tab = QWidget()
        self.config_layout = QVBoxLayout(self.config_tab)
        self.tabs.addTab(self.config_tab, "Settings")
        
        # Batch list tab
        self.batch_tab = QWidget()
        self.batch_layout = QVBoxLayout(self.batch_tab)
        self.tabs.addTab(self.batch_tab, "Batch Processing")
        
        self.top_layout.addWidget(self.tabs)
        
        # Bottom panel (text viewer)
        self.bottom_panel = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_panel)
        
        # Viewer panel title
        view_title = QLabel("Transcribed Text")
        view_title.setAlignment(Qt.AlignLeft)
        view_font = QFont()
        view_font.setBold(True)
        view_title.setFont(view_font)
        self.bottom_layout.addWidget(view_title)
        
        # Text viewer area (placeholder)
        self.text_view_placeholder = QLabel("Transcription will appear here")
        self.text_view_placeholder.setAlignment(Qt.AlignCenter)
        self.text_view_placeholder.setStyleSheet("color: #565f89;")
        self.bottom_layout.addWidget(self.text_view_placeholder)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.top_panel)
        self.main_splitter.addWidget(self.bottom_panel)
        
        # Set initial splitter sizes
        self.main_splitter.setSizes([400, 200])
    
    def resizeEvent(self, event):
        """
        Overrides the resize event to adjust components.
        """
        super().resizeEvent(event)
        # Additional layout adjustments can be made here


