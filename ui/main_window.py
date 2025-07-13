"""
Componente de interface principal para o aplicativo de transcrição.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QSplitter, QLabel, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

class MainWindow(QMainWindow):
    """
    Janela principal do aplicativo de transcrição.
    """
    def __init__(self):
        super().__init__()
        
        # Configuração da janela principal
        self.setWindowTitle("Whisper Transcriber")
        self.setMinimumSize(900, 600)
        
        # Carregar folha de estilo
        self._load_stylesheet()
        
        # Configurar widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Criar componentes da interface
        self._setup_ui()
        
        # Configurar barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")
    
    def _load_stylesheet(self):
        """
        Carrega a folha de estilo do tema azul escuro.
        """
        try:
            with open("ui/resources/style.qss", "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        except Exception as e:
            print(f"Erro ao carregar folha de estilo: {e}")
    
    def _setup_ui(self):
        """
        Configura os componentes da interface do usuário.
        """
        # Título do aplicativo
        title_label = QLabel("Whisper Transcriber")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.main_layout.addWidget(title_label)
        
        # Divisor principal
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.main_splitter)
        
        # Painel superior (entrada e configurações)
        self.top_panel = QWidget()
        self.top_layout = QVBoxLayout(self.top_panel)
        
        # Abas para entrada de mídia e configurações
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Aba de entrada de mídia
        self.media_input_tab = QWidget()
        self.media_input_layout = QVBoxLayout(self.media_input_tab)
        self.tabs.addTab(self.media_input_tab, "Entrada de Mídia")
        
        # Aba de configurações
        self.config_tab = QWidget()
        self.config_layout = QVBoxLayout(self.config_tab)
        self.tabs.addTab(self.config_tab, "Configurações")
        
        # Aba de lista de lote
        self.batch_tab = QWidget()
        self.batch_layout = QVBoxLayout(self.batch_tab)
        self.tabs.addTab(self.batch_tab, "Processamento em Lote")
        
        self.top_layout.addWidget(self.tabs)
        
        # Painel inferior (visualização de texto)
        self.bottom_panel = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_panel)
        
        # Título do painel de visualização
        view_title = QLabel("Texto Transcrito")
        view_title.setAlignment(Qt.AlignLeft)
        view_font = QFont()
        view_font.setBold(True)
        view_title.setFont(view_font)
        self.bottom_layout.addWidget(view_title)
        
        # Área de visualização de texto (placeholder)
        self.text_view_placeholder = QLabel("A transcrição aparecerá aqui")
        self.text_view_placeholder.setAlignment(Qt.AlignCenter)
        self.text_view_placeholder.setStyleSheet("color: #565f89;")
        self.bottom_layout.addWidget(self.text_view_placeholder)
        
        # Adicionar painéis ao splitter
        self.main_splitter.addWidget(self.top_panel)
        self.main_splitter.addWidget(self.bottom_panel)
        
        # Definir tamanhos iniciais do splitter
        self.main_splitter.setSizes([400, 200])
    
    def resizeEvent(self, event):
        """
        Sobrescreve o evento de redimensionamento para ajustar componentes.
        """
        super().resizeEvent(event)
        # Ajustes adicionais de layout podem ser feitos aqui
