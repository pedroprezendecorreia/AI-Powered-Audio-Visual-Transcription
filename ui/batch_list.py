"""
Componente de lista de processamento em lote para o aplicativo de transcrição.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal

class BatchList(QWidget):
    """
    Widget para gerenciar a lista de arquivos para processamento em lote.
    """
    # Sinais
    batch_process_requested = Signal(list)
    item_removed = Signal(int)
    folder_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title_label = QLabel("Lista de Arquivos para Processamento em Lote")
        self.layout.addWidget(title_label)
        
        # Botões de adição
        add_layout = QHBoxLayout()
        
        self.add_folder_button = QPushButton("Adicionar Pasta")
        self.add_folder_button.clicked.connect(self.on_add_folder_clicked)
        add_layout.addWidget(self.add_folder_button)
        
        add_layout.addStretch()
        
        self.layout.addLayout(add_layout)
        
        # Lista de arquivos
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.process_all_button = QPushButton("Processar Todos")
        self.process_all_button.clicked.connect(self.on_process_all_clicked)
        button_layout.addWidget(self.process_all_button)
        
        self.remove_selected_button = QPushButton("Remover Selecionado")
        self.remove_selected_button.clicked.connect(self.on_remove_selected_clicked)
        button_layout.addWidget(self.remove_selected_button)
        
        self.clear_all_button = QPushButton("Limpar Lista")
        self.clear_all_button.clicked.connect(self.on_clear_all_clicked)
        button_layout.addWidget(self.clear_all_button)
        
        self.layout.addLayout(button_layout)
        
        # Atualizar estado dos botões
        self._update_button_states()
    
    def add_item(self, path):
        """
        Adiciona um item à lista de lote.
        
        Args:
            path (str): Caminho do arquivo ou URL do YouTube
        """
        # Verificar se o item já existe na lista
        for i in range(self.file_list.count()):
            if self.file_list.item(i).text() == path:
                QMessageBox.information(
                    self,
                    "Item Duplicado",
                    "Este item já está na lista de processamento."
                )
                return
        
        # Adicionar novo item
        item = QListWidgetItem(path)
        self.file_list.addItem(item)
        
        # Atualizar estado dos botões
        self._update_button_states()
    
    def on_add_folder_clicked(self):
        """
        Manipulador para o clique no botão de adicionar pasta.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta com Arquivos de Áudio/Vídeo",
            ""
        )
        
        if folder_path:
            self.folder_selected.emit(folder_path)
    
    def on_process_all_clicked(self):
        """
        Manipulador para o clique no botão de processar todos.
        """
        if self.file_list.count() > 0:
            items = [self.file_list.item(i).text() for i in range(self.file_list.count())]
            self.batch_process_requested.emit(items)
    
    def on_remove_selected_clicked(self):
        """
        Manipulador para o clique no botão de remover selecionado.
        """
        selected_items = self.file_list.selectedItems()
        if selected_items:
            for item in selected_items:
                row = self.file_list.row(item)
                self.file_list.takeItem(row)
                self.item_removed.emit(row)
            
            # Atualizar estado dos botões
            self._update_button_states()
    
    def on_clear_all_clicked(self):
        """
        Manipulador para o clique no botão de limpar lista.
        """
        if self.file_list.count() > 0:
            confirm = QMessageBox.question(
                self,
                "Confirmar Limpeza",
                "Tem certeza que deseja limpar toda a lista?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.file_list.clear()
                # Atualizar estado dos botões
                self._update_button_states()
    
    def _update_button_states(self):
        """
        Atualiza o estado dos botões com base no conteúdo da lista.
        """
        has_items = self.file_list.count() > 0
        self.process_all_button.setEnabled(has_items)
        self.clear_all_button.setEnabled(has_items)
        
        has_selection = len(self.file_list.selectedItems()) > 0
        self.remove_selected_button.setEnabled(has_selection)
    
    def get_all_items(self):
        """
        Retorna todos os itens da lista.
        
        Returns:
            list: Lista de caminhos de arquivo/URLs
        """
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]
