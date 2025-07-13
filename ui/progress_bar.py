"""
Componente de barra de progresso e status para o aplicativo de transcrição.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class ProgressBar(QWidget):
    """
    Widget para exibir progresso e status das operações.
    """
    # Sinais
    cancel_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra de progresso principal
        self.progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_layout.addWidget(self.progress_bar, 1)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setEnabled(False)
        self.progress_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(self.progress_layout)
        
        # Status principal
        self.status_label = QLabel("Pronto")
        self.status_label.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setBold(True)
        self.status_label.setFont(font)
        self.layout.addWidget(self.status_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
        # Status detalhado
        self.detailed_status_label = QLabel("")
        self.detailed_status_label.setAlignment(Qt.AlignLeft)
        self.detailed_status_label.setWordWrap(True)
        self.layout.addWidget(self.detailed_status_label)
        
        # Indicador de atividade
        self.activity_indicator = QLabel("⏳")
        self.activity_indicator.setAlignment(Qt.AlignRight)
        self.activity_indicator.setVisible(False)
        self.layout.addWidget(self.activity_indicator)
        
        # Timer para animação do indicador de atividade
        self.animation_counter = 0
        self.animation_symbols = ["⏳", "⌛", "⏳", "⌛"]
    
    def set_progress(self, value, detailed_status=None):
        """
        Define o valor da barra de progresso.
        
        Args:
            value (int): Valor de progresso (0-100)
            detailed_status (str, optional): Status detalhado
        """
        self.progress_bar.setValue(value)
        
        if detailed_status:
            self.detailed_status_label.setText(detailed_status)
            
        # Atualizar indicador de atividade
        if value > 0 and value < 100:
            self.activity_indicator.setVisible(True)
            self.animation_counter = (self.animation_counter + 1) % len(self.animation_symbols)
            self.activity_indicator.setText(self.animation_symbols[self.animation_counter])
        else:
            self.activity_indicator.setVisible(False)
    
    def set_status(self, text):
        """
        Define o texto de status.
        
        Args:
            text (str): Texto de status
        """
        self.status_label.setText(text)
    
    def start_operation(self):
        """
        Inicia uma operação, habilitando o botão de cancelar.
        """
        self.cancel_button.setEnabled(True)
        self.activity_indicator.setVisible(True)
    
    def finish_operation(self):
        """
        Finaliza uma operação, desabilitando o botão de cancelar.
        """
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Pronto")
        self.detailed_status_label.setText("")
        self.activity_indicator.setVisible(False)
    
    def on_cancel_clicked(self):
        """
        Manipulador para o clique no botão de cancelar.
        """
        self.cancel_requested.emit()
