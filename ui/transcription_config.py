"""
Componente de configuração de transcrição para o aplicativo de transcrição.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal

class TranscriptionConfig(QWidget):
    """
    Widget para configurações de transcrição (idioma, modelo, dispositivo).
    """
    # Sinais
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Configuração de idioma
        self.setup_language_section()
        
        # Configuração de modelo
        self.setup_model_section()
        
        # Configuração de dispositivo
        self.setup_device_section()
        
        # Adicionar espaçador para empurrar tudo para cima
        self.layout.addStretch()
        
        # Configuração inicial
        self.current_config = {
            'language': 'auto',
            'model': 'base',
            'device': 'cuda' if self.cuda_radio.isChecked() else 'cpu'
        }
    
    def setup_language_section(self):
        """
        Configura a seção de seleção de idioma.
        """
        language_group = QGroupBox("Idioma")
        language_layout = QVBoxLayout(language_group)
        
        # Descrição
        language_desc = QLabel("Selecione o idioma do áudio ou escolha detecção automática:")
        language_layout.addWidget(language_desc)
        
        # Combobox de idiomas
        self.language_combo = QComboBox()
        self.language_combo.addItem("Detecção Automática", "auto")
        self.language_combo.addItem("Português", "pt")
        self.language_combo.addItem("Inglês", "en")
        self.language_combo.addItem("Espanhol", "es")
        self.language_combo.addItem("Francês", "fr")
        self.language_combo.addItem("Alemão", "de")
        self.language_combo.addItem("Italiano", "it")
        self.language_combo.addItem("Japonês", "ja")
        self.language_combo.addItem("Chinês", "zh")
        self.language_combo.addItem("Russo", "ru")
        self.language_combo.addItem("Árabe", "ar")
        
        self.language_combo.currentIndexChanged.connect(self.on_config_changed)
        language_layout.addWidget(self.language_combo)
        
        # Adicionar ao layout principal
        self.layout.addWidget(language_group)
    
    def setup_model_section(self):
        """
        Configura a seção de seleção de modelo.
        """
        model_group = QGroupBox("Modelo")
        model_layout = QVBoxLayout(model_group)
        
        # Descrição
        model_desc = QLabel("Selecione o modelo Whisper a ser utilizado:")
        model_layout.addWidget(model_desc)
        
        # Combobox de modelos
        self.model_combo = QComboBox()
        self.model_combo.addItem("Tiny (velocidade rápida, menor precisão)", "tiny")
        self.model_combo.addItem("Base (equilíbrio entre velocidade e precisão)", "base")
        self.model_combo.addItem("Small (boa precisão, velocidade moderada)", "small")
        self.model_combo.addItem("Medium (alta precisão, velocidade lenta)", "medium")
        self.model_combo.addItem("Large (máxima precisão, velocidade muito lenta)", "large")
        
        # Definir o modelo "base" como padrão (índice 1)
        self.model_combo.setCurrentIndex(1)
        
        self.model_combo.currentIndexChanged.connect(self.on_config_changed)
        model_layout.addWidget(self.model_combo)
        
        # Adicionar ao layout principal
        self.layout.addWidget(model_group)
    
    def setup_device_section(self):
        """
        Configura a seção de seleção de dispositivo.
        """
        device_group = QGroupBox("Dispositivo de Processamento")
        device_layout = QVBoxLayout(device_group)
        
        # Descrição
        device_desc = QLabel("Selecione o dispositivo para processamento:")
        device_layout.addWidget(device_desc)
        
        # Opções de dispositivo
        self.device_button_group = QButtonGroup(self)
        
        device_layout_h = QHBoxLayout()
        
        self.cuda_radio = QRadioButton("GPU (CUDA)")
        self.cuda_radio.setChecked(True)  # GPU como padrão
        self.device_button_group.addButton(self.cuda_radio)
        device_layout_h.addWidget(self.cuda_radio)
        
        self.cpu_radio = QRadioButton("CPU")
        self.device_button_group.addButton(self.cpu_radio)
        device_layout_h.addWidget(self.cpu_radio)
        
        device_layout.addLayout(device_layout_h)
        
        # Conectar sinais
        self.cuda_radio.toggled.connect(self.on_config_changed)
        self.cpu_radio.toggled.connect(self.on_config_changed)
        
        # Adicionar ao layout principal
        self.layout.addWidget(device_group)
    
    def on_config_changed(self):
        """
        Manipulador para mudanças nas configurações.
        """
        self.current_config = {
            'language': self.language_combo.currentData(),
            'model': self.model_combo.currentData(),
            'device': 'cuda' if self.cuda_radio.isChecked() else 'cpu'
        }
        
        self.config_changed.emit(self.current_config)
    
    def get_config(self):
        """
        Retorna a configuração atual.
        
        Returns:
            dict: Configuração atual
        """
        return self.current_config
