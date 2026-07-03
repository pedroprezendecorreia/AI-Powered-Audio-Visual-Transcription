"""
Transcription configuration component for the transcription application.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal

class TranscriptionConfig(QWidget):
    """
    Widget for transcription settings (language, model, device).
    """
    # Signals
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Language configuration
        self.setup_language_section()
        
        # Model configuration
        self.setup_model_section()
        
        # Device configuration
        self.setup_device_section()
        
        # Add spacer to push everything up
        self.layout.addStretch()
        
        # Initial configuration
        self.current_config = {
            'language': 'auto',
            'model': 'base',
            'device': 'cuda' if self.cuda_radio.isChecked() else 'cpu'
        }
    
    def setup_language_section(self):
        """
        Sets up the language selection section.
        """
        language_group = QGroupBox("Language")
        language_layout = QVBoxLayout(language_group)
        language_layout.setContentsMargins(6, 10, 6, 6)
        language_layout.setSpacing(10)

        # Description
        language_desc = QLabel("Select the audio language or choose automatic detection:")
        language_desc.setWordWrap(True)
        language_layout.addWidget(language_desc)
        
        # Language combobox
        self.language_combo = QComboBox()
        self.language_combo.addItem("Automatic Detection", "auto")
        self.language_combo.addItem("Portuguese", "pt")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Spanish", "es")
        self.language_combo.addItem("French", "fr")
        self.language_combo.addItem("German", "de")
        self.language_combo.addItem("Italian", "it")
        self.language_combo.addItem("Japanese", "ja")
        self.language_combo.addItem("Chinese", "zh")
        self.language_combo.addItem("Russian", "ru")
        self.language_combo.addItem("Arabic", "ar")
        
        self.language_combo.currentIndexChanged.connect(self.on_config_changed)
        language_layout.addWidget(self.language_combo)
        
        # Add to main layout
        self.layout.addWidget(language_group)
    
    def setup_model_section(self):
        """
        Sets up the model selection section.
        """
        model_group = QGroupBox("Model")
        model_layout = QVBoxLayout(model_group)
        model_layout.setContentsMargins(6, 10, 6, 6)
        model_layout.setSpacing(10)

        # Description
        model_desc = QLabel("Select the Whisper model to be used:")
        model_desc.setWordWrap(True)
        model_layout.addWidget(model_desc)
        
        # Model combobox
        self.model_combo = QComboBox()
        self.model_combo.addItem("Tiny (fast speed, lower accuracy)", "tiny")
        self.model_combo.addItem("Base (balance of speed and accuracy)", "base")
        self.model_combo.addItem("Small (good accuracy, moderate speed)", "small")
        self.model_combo.addItem("Medium (high accuracy, slow speed)", "medium")
        self.model_combo.addItem("Large (maximum accuracy, very slow speed)", "large")
        
        # Set "base" model as default (index 1)
        self.model_combo.setCurrentIndex(1)
        
        self.model_combo.currentIndexChanged.connect(self.on_config_changed)
        model_layout.addWidget(self.model_combo)
        
        # Add to main layout
        self.layout.addWidget(model_group)
    
    def setup_device_section(self):
        """
        Sets up the device selection section.
        """
        device_group = QGroupBox("Processing Device")
        device_layout = QVBoxLayout(device_group)
        device_layout.setContentsMargins(6, 10, 6, 6)
        device_layout.setSpacing(10)

        # Description
        device_desc = QLabel("Select the device for processing (GPU requires an NVIDIA card):")
        device_desc.setWordWrap(True)
        device_layout.addWidget(device_desc)
        
        # Device options
        self.device_button_group = QButtonGroup(self)
        
        device_layout_h = QHBoxLayout()
        
        self.cpu_radio = QRadioButton("CPU")
        self.cpu_radio.setChecked(True)  # CPU as default (works everywhere)
        self.device_button_group.addButton(self.cpu_radio)
        device_layout_h.addWidget(self.cpu_radio)

        self.cuda_radio = QRadioButton("GPU (NVIDIA CUDA)")
        self.device_button_group.addButton(self.cuda_radio)
        device_layout_h.addWidget(self.cuda_radio)
        
        device_layout.addLayout(device_layout_h)
        
        # Connect signals
        self.cuda_radio.toggled.connect(self.on_config_changed)
        self.cpu_radio.toggled.connect(self.on_config_changed)
        
        # Add to main layout
        self.layout.addWidget(device_group)
    
    def on_config_changed(self):
        """
        Handler for configuration changes.
        """
        self.current_config = {
            'language': self.language_combo.currentData(),
            'model': self.model_combo.currentData(),
            'device': 'cuda' if self.cuda_radio.isChecked() else 'cpu'
        }
        
        self.config_changed.emit(self.current_config)
    
    def get_config(self):
        """
        Returns the current configuration.
        
        Returns:
            dict: Current configuration
        """
        return self.current_config


