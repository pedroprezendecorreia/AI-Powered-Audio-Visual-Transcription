"""
Módulo de processamento em lote para o aplicativo de transcrição.
"""
import os
import threading
from queue import Queue
from pathlib import Path
from PySide6.QtCore import QObject, Signal

class BatchProcessorSignals(QObject):
    """
    Sinais para comunicação com a interface durante o processamento em lote.
    """
    item_completed = Signal(int, str, str)  # índice, caminho, texto
    batch_progress = Signal(int, str)  # porcentagem, mensagem
    item_progress = Signal(int, int, str)  # índice, porcentagem, mensagem
    batch_completed = Signal(dict)  # resultados
    error_occurred = Signal(str)  # mensagem de erro
    confirmation_needed = Signal(int, str, str)  # índice, caminho, texto

class BatchProcessor:
    """
    Classe para gerenciamento de processamento em lote.
    """
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.batch_thread = None
        self.is_processing = False
        self.cancel_requested = False
        self.pause_requested = False
        self.current_item_index = -1
        self.items_queue = Queue()
        self.results = {}
        self.signals = BatchProcessorSignals()
        self.waiting_confirmation = False
    
    def process_batch(self, items, config):
        """
        Inicia o processamento em lote.
        
        Args:
            items (list): Lista de itens (caminhos de arquivo)
            config (dict): Configurações de transcrição
        """
        if self.is_processing:
            self.signals.error_occurred.emit("Já existe um processamento em lote em andamento.")
            return
        
        self.is_processing = True
        self.cancel_requested = False
        self.pause_requested = False
        self.current_item_index = -1
        self.results = {}
        self.waiting_confirmation = False
        
        # Limpar e preencher a fila
        while not self.items_queue.empty():
            self.items_queue.get()
        
        for item in items:
            self.items_queue.put(item)
        
        # Iniciar thread de processamento em lote
        self.batch_thread = threading.Thread(
            target=self._batch_thread,
            args=(items, config)
        )
        self.batch_thread.daemon = True
        self.batch_thread.start()
    
    def _batch_thread(self, items, config):
        """
        Thread de processamento em lote.
        
        Args:
            items (list): Lista de itens (caminhos de arquivo)
            config (dict): Configurações de transcrição
        """
        try:
            total_items = len(items)
            processed_items = 0
            
            while not self.items_queue.empty() and not self.cancel_requested:
                # Obter próximo item
                item = self.items_queue.get()
                self.current_item_index += 1
                
                # Atualizar progresso do lote
                batch_progress = int((processed_items / total_items) * 100)
                self.signals.batch_progress.emit(
                    batch_progress, 
                    f"Processando item {processed_items + 1} de {total_items}: {os.path.basename(item)}"
                )
                
                # Processar arquivo de mídia
                self._process_media_file(item, config)
                
                # Aguardar confirmação antes de prosseguir
                self.waiting_confirmation = True
                while self.waiting_confirmation and not self.cancel_requested:
                    # Esperar pela confirmação do usuário
                    threading.Event().wait(0.1)
                
                processed_items += 1
                
                # Verificar cancelamento após cada item
                if self.cancel_requested:
                    break
            
            # Finalizar processamento em lote
            if not self.cancel_requested:
                self.signals.batch_completed.emit(self.results)
        
        except Exception as e:
            self.signals.error_occurred.emit(f"Erro no processamento em lote: {str(e)}")
        
        finally:
            self.is_processing = False
    
    def _process_media_file(self, file_path, config):
        """
        Processa um arquivo de mídia.
        
        Args:
            file_path (str): Caminho do arquivo de mídia
            config (dict): Configurações de transcrição
        """
        if not os.path.isfile(file_path):
            self.signals.error_occurred.emit(f"Arquivo não encontrado: {file_path}")
            return
        
        self.signals.item_progress.emit(self.current_item_index, 0, "Iniciando transcrição...")
        
        # Configurar callbacks para transcrição
        def transcribe_progress(percent, status=None):
            self.signals.item_progress.emit(
                self.current_item_index, 
                percent, 
                status or f"Transcrição: {percent}%"
            )
        
        def transcribe_complete(text):
            self.signals.item_progress.emit(self.current_item_index, 100, "Transcrição concluída")
            
            # Armazenar resultado
            self.results[file_path] = text
            
            # Solicitar confirmação do usuário
            self.signals.confirmation_needed.emit(self.current_item_index, file_path, text)
        
        def transcribe_error(error_msg):
            self.signals.error_occurred.emit(error_msg)
            # Passar para o próximo item
            self.waiting_confirmation = False
        
        # Iniciar transcrição
        self.transcriber.transcribe(
            file_path,
            config,
            progress_callback=transcribe_progress,
            completion_callback=transcribe_complete,
            error_callback=transcribe_error
        )
    
    def confirm_and_continue(self, save=True, file_path=None, text=None):
        """
        Confirma o processamento do item atual e continua para o próximo.
        
        Args:
            save (bool): Se True, salva o arquivo de texto
            file_path (str): Caminho do arquivo processado
            text (str): Texto transcrito
        """
        if save and file_path and text:
            try:
                # Determinar o diretório e nome do arquivo
                output_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.txt")
                
                # Salvar o arquivo
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # Notificar conclusão do item
                self.signals.item_completed.emit(self.current_item_index, file_path, output_path)
            except Exception as e:
                self.signals.error_occurred.emit(f"Erro ao salvar arquivo: {str(e)}")
        
        # Continuar para o próximo item
        self.waiting_confirmation = False
    
    def cancel(self):
        """
        Cancela o processamento em lote.
        
        Returns:
            bool: True se o cancelamento foi iniciado, False caso contrário
        """
        if self.is_processing:
            self.cancel_requested = True
            self.waiting_confirmation = False
            
            # Cancelar operações em andamento
            if self.transcriber.is_transcribing:
                self.transcriber.cancel()
            
            return True
        
        return False
    
    def cancel_item(self, index):
        """
        Cancela um item específico do lote.
        
        Args:
            index (int): Índice do item a ser cancelado
            
        Returns:
            bool: True se o cancelamento foi iniciado, False caso contrário
        """
        if self.is_processing and index == self.current_item_index:
            # Cancelar operação atual
            if self.transcriber.is_transcribing:
                self.transcriber.cancel()
            
            # Passar para o próximo item
            self.waiting_confirmation = False
            
            return True
        
        return False
