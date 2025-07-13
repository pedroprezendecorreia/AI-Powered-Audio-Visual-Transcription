"""
Arquivo principal do aplicativo de transcrição.
"""
import sys
import os
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool

from ui.main_window import MainWindow
from ui.media_input import MediaInput
from ui.batch_list import BatchList
from ui.transcription_config import TranscriptionConfig
from ui.progress_bar import ProgressBar
from ui.text_viewer import TextView

from core.transcriber import Transcriber
from core.batch_processor import BatchProcessor
from core.file_manager import FileManager

class ApplicationController(QObject):
    """
    Controlador principal do aplicativo, gerenciando a comunicação entre UI e backend.
    """
    # Sinais para atualização da UI
    update_progress = Signal(int, str)
    update_status = Signal(str)
    update_text_view = Signal(str)
    processing_started = Signal()
    processing_finished = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Inicializar componentes de backend
        self.transcriber = Transcriber()
        self.batch_processor = BatchProcessor(self.transcriber)
        self.file_manager = FileManager()
        
        # Configuração atual
        self.current_config = {
            'language': 'auto',
            'model': 'base',
            'device': 'cuda'
        }
        
        # Thread pool para operações em background
        self.thread_pool = QThreadPool()
        
        # Conectar sinais do processador em lote
        self.batch_processor.signals.item_progress.connect(self.on_batch_item_progress)
        self.batch_processor.signals.batch_progress.connect(self.on_batch_progress)
        self.batch_processor.signals.item_completed.connect(self.on_batch_item_completed)
        self.batch_processor.signals.batch_completed.connect(self.on_batch_completed)
        self.batch_processor.signals.error_occurred.connect(self.on_batch_error)
        self.batch_processor.signals.confirmation_needed.connect(self.on_confirmation_needed)
    
    def setup_main_window(self, main_window):
        """
        Configura a janela principal e conecta sinais e slots.
        
        Args:
            main_window (MainWindow): Janela principal do aplicativo
        """
        self.main_window = main_window
        
        # Inicializar componentes da UI
        self.setup_media_input()
        self.setup_batch_list()
        self.setup_transcription_config()
        self.setup_progress_bar()
        self.setup_text_viewer()
        
        # Conectar sinais globais
        self.update_progress.connect(self.progress_bar.set_progress)
        self.update_status.connect(self.main_window.status_bar.showMessage)
        self.update_text_view.connect(self.text_viewer.set_text)
        self.processing_started.connect(self.progress_bar.start_operation)
        self.processing_finished.connect(self.progress_bar.finish_operation)
    
    def setup_media_input(self):
        """
        Configura o componente de entrada de mídia.
        """
        self.media_input = MediaInput()
        self.main_window.media_input_layout.addWidget(self.media_input)
        
        # Conectar sinais
        self.media_input.file_selected.connect(self.transcribe_file)
        self.media_input.folder_selected.connect(self.add_folder_to_batch)
        self.media_input.add_to_batch.connect(self.add_to_batch)
    
    def setup_batch_list(self):
        """
        Configura o componente de lista de lote.
        """
        self.batch_list = BatchList()
        self.main_window.batch_layout.addWidget(self.batch_list)
        
        # Conectar sinais
        self.batch_list.batch_process_requested.connect(self.process_batch)
        self.batch_list.folder_selected.connect(self.add_folder_to_batch)
    
    def setup_transcription_config(self):
        """
        Configura o componente de configurações de transcrição.
        """
        self.transcription_config = TranscriptionConfig()
        self.main_window.config_layout.addWidget(self.transcription_config)
        
        # Conectar sinais
        self.transcription_config.config_changed.connect(self.update_config)
    
    def setup_progress_bar(self):
        """
        Configura o componente de barra de progresso.
        """
        self.progress_bar = ProgressBar()
        self.main_window.main_layout.addWidget(self.progress_bar)
        
        # Conectar sinais
        self.progress_bar.cancel_requested.connect(self.cancel_operation)
    
    def setup_text_viewer(self):
        """
        Configura o componente de visualização de texto.
        """
        self.text_viewer = TextView()
        self.main_window.bottom_layout.addWidget(self.text_viewer)
        
        # Remover placeholder
        if hasattr(self.main_window, 'text_view_placeholder'):
            self.main_window.text_view_placeholder.setParent(None)
            self.main_window.text_view_placeholder = None
    
    @Slot(dict)
    def update_config(self, config):
        """
        Atualiza a configuração atual.
        
        Args:
            config (dict): Nova configuração
        """
        self.current_config = config
    
    @Slot(str)
    def transcribe_file(self, file_path):
        """
        Inicia a transcrição de um arquivo.
        
        Args:
            file_path (str): Caminho do arquivo
        """
        if not file_path:
            return
        
        if not os.path.isfile(file_path):
            self.update_status.emit(f"Arquivo não encontrado: {file_path}")
            return
        
        self.processing_started.emit()
        self.update_status.emit(f"Iniciando transcrição: {file_path}")
        
        # Configurar callbacks
        def progress_callback(percent, status=None):
            self.update_progress.emit(percent, status or f"Transcrição: {percent}%")
        
        def completion_callback(text):
            self.update_status.emit("Transcrição concluída")
            self.update_text_view.emit(text)
            
            # Salvar automaticamente o arquivo de texto
            try:
                output_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.txt")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                self.update_status.emit(f"Transcrição salva em: {output_path}")
            except Exception as e:
                self.update_status.emit(f"Erro ao salvar transcrição: {str(e)}")
            
            self.processing_finished.emit()
        
        def error_callback(error_msg):
            self.update_status.emit(f"Erro: {error_msg}")
            self.processing_finished.emit()
        
        # Iniciar transcrição
        self.transcriber.transcribe(
            file_path,
            self.current_config,
            progress_callback=progress_callback,
            completion_callback=completion_callback,
            error_callback=error_callback
        )
    
    @Slot(str)
    def add_folder_to_batch(self, folder_path):
        """
        Adiciona todos os arquivos de mídia de uma pasta ao lote.
        
        Args:
            folder_path (str): Caminho da pasta
        """
        if not folder_path or not os.path.isdir(folder_path):
            self.update_status.emit("Pasta inválida")
            return
        
        # Encontrar todos os arquivos de mídia na pasta
        media_files = self.file_manager.find_media_files_in_folder(folder_path)
        
        # Adicionar arquivos ao lote
        if media_files:
            for file_path in media_files:
                self.batch_list.add_item(file_path)
            
            self.update_status.emit(f"Adicionados {len(media_files)} arquivos ao lote")
        else:
            self.update_status.emit("Nenhum arquivo de mídia encontrado na pasta")
    
    @Slot(str)
    def add_to_batch(self, item):
        """
        Adiciona um item à lista de lote.
        
        Args:
            item (str): Item a ser adicionado (caminho de arquivo)
        """
        if not item:
            return
        
        # Verificar se é um arquivo local
        is_file = os.path.isfile(item)
        
        if not is_file:
            self.update_status.emit("Item inválido para processamento em lote")
            return
        
        # Adicionar à lista
        self.batch_list.add_item(item)
        self.update_status.emit(f"Item adicionado ao lote: {item}")
    
    @Slot(list)
    def process_batch(self, items):
        """
        Inicia o processamento em lote.
        
        Args:
            items (list): Lista de itens a serem processados
        """
        if not items:
            return
        
        self.processing_started.emit()
        self.update_status.emit(f"Iniciando processamento em lote: {len(items)} itens")
        
        # Iniciar processamento em lote
        self.batch_processor.process_batch(items, self.current_config)
    
    @Slot(int, int, str)
    def on_batch_item_progress(self, index, percent, status):
        """
        Manipulador para progresso de item individual em lote.
        
        Args:
            index (int): Índice do item
            percent (int): Porcentagem de progresso
            status (str): Mensagem de status
        """
        self.update_progress.emit(percent, f"Item {index + 1}: {status}")
    
    @Slot(int, str)
    def on_batch_progress(self, percent, status):
        """
        Manipulador para progresso geral do lote.
        
        Args:
            percent (int): Porcentagem de progresso
            status (str): Mensagem de status
        """
        self.update_status.emit(status)
    
    @Slot(int, str, str)
    def on_batch_item_completed(self, index, file_path, output_path):
        """
        Manipulador para conclusão de item individual em lote.
        
        Args:
            index (int): Índice do item
            file_path (str): Caminho do arquivo processado
            output_path (str): Caminho do arquivo de saída
        """
        file_name = os.path.basename(file_path)
        self.update_status.emit(f"Transcrição salva em: {output_path}")
        
        # Limpar a área de visualização
        self.update_text_view.emit("")
        
        # Notificar que está prosseguindo para o próximo item
        if self.batch_processor.current_item_index < len(self.batch_list.get_all_items()) - 1:
            next_file = self.batch_list.get_all_items()[self.batch_processor.current_item_index + 1]
            next_file_name = os.path.basename(next_file)
            self.update_status.emit(f"Prosseguindo para o próximo item: {next_file_name}")
    
    @Slot(dict)
    def on_batch_completed(self, results):
        """
        Manipulador para conclusão do lote.
        
        Args:
            results (dict): Resultados do processamento em lote
        """
        self.update_status.emit(f"Processamento em lote concluído: {len(results)} itens")
        self.processing_finished.emit()
    
    @Slot(str)
    def on_batch_error(self, error_msg):
        """
        Manipulador para erros no processamento em lote.
        
        Args:
            error_msg (str): Mensagem de erro
        """
        self.update_status.emit(f"Erro: {error_msg}")
    
    @Slot(int, str, str)
    def on_confirmation_needed(self, index, file_path, text):
        """
        Manipulador para solicitação de confirmação.
        
        Args:
            index (int): Índice do item
            file_path (str): Caminho do arquivo processado
            text (str): Texto transcrito
        """
        # Mostrar o texto transcrito
        self.update_text_view.emit(text)
        
        # Mostrar caixa de diálogo de confirmação
        file_name = os.path.basename(file_path)
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("Confirmação de Transcrição")
        msg_box.setText(f"A transcrição do arquivo '{file_name}' foi concluída.")
        msg_box.setInformativeText("Deseja salvar esta transcrição e continuar para o próximo item?")
        
        # Botões em português
        btn_save_continue = msg_box.addButton("Salvar e Continuar", QMessageBox.YesRole)
        btn_save_stop = msg_box.addButton("Salvar e Parar", QMessageBox.NoRole)
        btn_cancel = msg_box.addButton("Cancelar", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(btn_save_continue)
        
        # Adicionar detalhes sobre o arquivo
        details = f"Arquivo: {file_path}\n"
        details += f"Tamanho da transcrição: {len(text)} caracteres\n"
        details += f"Primeiras 100 caracteres: {text[:100]}..."
        msg_box.setDetailedText(details)
        
        # Executar caixa de diálogo
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == btn_save_continue:
            # Salvar e continuar
            self.batch_processor.confirm_and_continue(True, file_path, text)
        elif clicked_button == btn_save_stop:
            # Salvar e parar o processamento
            self.batch_processor.confirm_and_continue(True, file_path, text)
            # Cancelar o processamento em lote após salvar o item atual
            self.cancel_operation()
        else:  # btn_cancel
            # Cancelar o processamento em lote
            self.cancel_operation()
    
    @Slot()
    def cancel_operation(self):
        """
        Cancela a operação em andamento.
        """
        # Tentar cancelar operações em andamento
        if self.transcriber.is_transcribing:
            self.transcriber.cancel()
            self.update_status.emit("Transcrição cancelada")
        
        if self.batch_processor.is_processing:
            self.batch_processor.cancel()
            self.update_status.emit("Processamento em lote cancelado")
        
        self.processing_finished.emit()

def main():
    """
    Função principal do aplicativo.
    """
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    
    # Criar janela principal
    main_window = MainWindow()
    
    # Criar controlador
    controller = ApplicationController()
    controller.setup_main_window(main_window)
    
    # Exibir janela
    main_window.show()
    
    # Executar loop de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
