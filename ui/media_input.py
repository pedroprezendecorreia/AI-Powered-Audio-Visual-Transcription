"""
Componente de entrada de mídia para o aplicativo de transcrição.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QGroupBox
)
from PySide6.QtCore import Qt, Signal

class MediaInput(QWidget):
    """
    Widget para entrada de mídia (arquivo local).
    """
    # Sinais
    file_selected = Signal(str)
    folder_selected = Signal(str)
    add_to_batch = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Seção de entrada de arquivo local
        self.setup_file_section()
    
    def setup_file_section(self):
        """
        Configura a seção de seleção de arquivo local.
        """
        file_group = QGroupBox("Arquivo Local")
        file_layout = QVBoxLayout(file_group)
        
        # Descrição
        file_desc = QLabel("Selecione um arquivo de áudio ou vídeo do seu computador:")
        file_layout.addWidget(file_desc)
        
        # Campo de entrada e botão
        file_input_layout = QHBoxLayout()
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Caminho do arquivo...")
        self.file_path_input.setReadOnly(True)
        file_input_layout.addWidget(self.file_path_input, 1)
        
        self.browse_button = QPushButton("Procurar Arquivo")
        self.browse_button.clicked.connect(self.on_browse_clicked)
        file_input_layout.addWidget(self.browse_button)
        
        self.browse_folder_button = QPushButton("Procurar Pasta")
        self.browse_folder_button.clicked.connect(self.on_browse_folder_clicked)
        file_input_layout.addWidget(self.browse_folder_button)
        
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        file_input_layout.addWidget(self.clear_button)
        
        file_layout.addLayout(file_input_layout)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        
        self.transcribe_button = QPushButton("Transcrever")
        self.transcribe_button.clicked.connect(self.on_transcribe_clicked)
        action_layout.addWidget(self.transcribe_button)
        
        self.add_to_batch_file_button = QPushButton("Adicionar ao Lote")
        self.add_to_batch_file_button.clicked.connect(self.on_add_to_batch_file_clicked)
        action_layout.addWidget(self.add_to_batch_file_button)
        
        file_layout.addLayout(action_layout)
        
        # Adicionar ao layout principal
        self.layout.addWidget(file_group)
        
        # Adicionar espaçador para empurrar tudo para cima
        self.layout.addStretch()
    
    def on_browse_clicked(self):
        """
        Manipulador para o clique no botão de procurar arquivo.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo de Áudio/Vídeo",
            "",
            "Arquivos de Mídia (*.mp3 *.mp4 *.wav *.ogg *.flac *.avi *.mov *.mkv *.webm);;Todos os Arquivos (*)"
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
            self.file_selected.emit(file_path)
    
    def on_browse_folder_clicked(self):
        """
        Manipulador para o clique no botão de procurar pasta.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta com Arquivos de Áudio/Vídeo",
            ""
        )
        
        if folder_path:
            self.file_path_input.setText(folder_path)
            self.folder_selected.emit(folder_path)
    
    def on_clear_clicked(self):
        """
        Manipulador para o clique no botão de limpar.
        """
        self.file_path_input.clear()
    
    def on_transcribe_clicked(self):
        """
        Manipulador para o clique no botão de transcrever.
        """
        file_path = self.file_path_input.text()
        if file_path:
            self.file_selected.emit(file_path)
    
    def on_add_to_batch_file_clicked(self):
        """
        Manipulador para o clique no botão de adicionar arquivo ao lote.
        """
        file_path = self.file_path_input.text()
        if file_path:
            self.add_to_batch.emit(file_path)
