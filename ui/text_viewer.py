"""
Componente de visualização de texto para o aplicativo de transcrição.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QClipboard, QGuiApplication

class TextView(QWidget):
    """
    Widget para visualização e exportação do texto transcrito.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de texto
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("A transcrição aparecerá aqui")
        self.layout.addWidget(self.text_edit, 1)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("Copiar para Área de Transferência")
        self.copy_button.clicked.connect(self.on_copy_clicked)
        button_layout.addWidget(self.copy_button)
        
        self.save_button = QPushButton("Salvar como TXT")
        self.save_button.clicked.connect(self.on_save_clicked)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self.on_clear_clicked)
        button_layout.addWidget(self.clear_button)
        
        self.layout.addLayout(button_layout)
        
        # Atualizar estado dos botões
        self._update_button_states()
    
    def set_text(self, text):
        """
        Define o texto a ser exibido.
        
        Args:
            text (str): Texto transcrito
        """
        self.text_edit.setPlainText(text)
        self._update_button_states()
    
    def get_text(self):
        """
        Retorna o texto atual.
        
        Returns:
            str: Texto atual
        """
        return self.text_edit.toPlainText()
    
    def on_copy_clicked(self):
        """
        Manipulador para o clique no botão de copiar.
        """
        text = self.text_edit.toPlainText()
        if text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(
                self,
                "Copiado",
                "Texto copiado para a área de transferência."
            )
    
    def on_save_clicked(self):
        """
        Manipulador para o clique no botão de salvar.
        """
        text = self.text_edit.toPlainText()
        if text:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Transcrição",
                "",
                "Arquivos de Texto (*.txt)"
            )
            
            if file_path:
                # Adicionar extensão .txt se não estiver presente
                if not file_path.lower().endswith('.txt'):
                    file_path += '.txt'
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    QMessageBox.information(
                        self,
                        "Salvo",
                        f"Transcrição salva em {file_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Erro",
                        f"Erro ao salvar arquivo: {str(e)}"
                    )
    
    def on_clear_clicked(self):
        """
        Manipulador para o clique no botão de limpar.
        """
        if self.text_edit.toPlainText():
            confirm = QMessageBox.question(
                self,
                "Confirmar Limpeza",
                "Tem certeza que deseja limpar o texto?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.text_edit.clear()
                self._update_button_states()
    
    def _update_button_states(self):
        """
        Atualiza o estado dos botões com base no conteúdo do texto.
        """
        has_text = bool(self.text_edit.toPlainText())
        self.copy_button.setEnabled(has_text)
        self.save_button.setEnabled(has_text)
        self.clear_button.setEnabled(has_text)
