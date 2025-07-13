"""
Módulo de transcrição usando a API Whisper da OpenAI.
"""
import os
import torch
import whisper
import threading
import time
from pathlib import Path

class Transcriber:
    """
    Classe para transcrição de áudio usando a API Whisper da OpenAI.
    """
    def __init__(self):
        self.transcription_thread = None
        self.is_transcribing = False
        self.model = None
        self.current_model_name = None
        self.cancel_requested = False
        self.start_time = 0
        self.estimated_total_time = 0
    
    def transcribe(self, file_path, config, progress_callback=None, completion_callback=None, error_callback=None):
        """
        Inicia a transcrição de um arquivo de áudio.
        
        Args:
            file_path (str): Caminho do arquivo de áudio
            config (dict): Configurações de transcrição (idioma, modelo, dispositivo)
            progress_callback (callable): Função de callback para atualização de progresso
            completion_callback (callable): Função de callback para conclusão da transcrição
            error_callback (callable): Função de callback para erros
        """
        if self.is_transcribing:
            if error_callback:
                error_callback("Já existe uma transcrição em andamento.")
            return
        
        self.is_transcribing = True
        self.cancel_requested = False
        self.start_time = time.time()
        self.estimated_total_time = 0
        
        # Iniciar thread de transcrição
        self.transcription_thread = threading.Thread(
            target=self._transcribe_thread,
            args=(file_path, config, progress_callback, completion_callback, error_callback)
        )
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def _transcribe_thread(self, file_path, config, progress_callback, completion_callback, error_callback):
        """
        Thread de transcrição.
        
        Args:
            file_path (str): Caminho do arquivo de áudio
            config (dict): Configurações de transcrição (idioma, modelo, dispositivo)
            progress_callback (callable): Função de callback para atualização de progresso
            completion_callback (callable): Função de callback para conclusão da transcrição
            error_callback (callable): Função de callback para erros
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.isfile(file_path):
                if error_callback:
                    error_callback(f"Arquivo não encontrado: {file_path}")
                return
            
            # Extrair configurações
            model_name = config.get('model', 'base')
            language = config.get('language', 'auto')
            device = config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu')
            
            # Verificar disponibilidade de GPU
            if device == 'cuda' and not torch.cuda.is_available():
                if progress_callback:
                    progress_callback(0, "GPU não disponível, usando CPU")
                device = 'cpu'
            
            # Carregar modelo se necessário
            if progress_callback:
                progress_callback(10, f"Carregando modelo {model_name}...")
            
            # Carregar novo modelo apenas se for diferente do atual
            if self.model is None or self.current_model_name != model_name:
                self.model = whisper.load_model(model_name, device=device)
                self.current_model_name = model_name
            
            if self.cancel_requested:
                return
            
            # Configurar opções de transcrição
            transcribe_options = {}
            
            # Definir idioma se não for automático
            if language != 'auto':
                transcribe_options['language'] = language
            
            # Configurar fp16 com base no dispositivo
            transcribe_options['fp16'] = (device == 'cuda')
            
            # Estimar tempo total com base no tamanho do arquivo e modelo
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Fatores de estimativa de tempo por modelo (segundos por MB)
            time_factors = {
                'tiny': 1.0,
                'base': 2.0,
                'small': 4.0,
                'medium': 8.0,
                'large': 16.0
            }
            
            # Ajustar fator com base no dispositivo
            device_factor = 1.0 if device == 'cuda' else 3.0
            
            # Calcular estimativa de tempo
            self.estimated_total_time = file_size_mb * time_factors.get(model_name, 2.0) * device_factor
            
            if progress_callback:
                elapsed_time = time.time() - self.start_time
                remaining_time = max(0, self.estimated_total_time - elapsed_time)
                progress_callback(30, f"Iniciando transcrição... Tempo estimado: {format_time(self.estimated_total_time)}")
            
            # Realizar transcrição
            result = self.model.transcribe(file_path, **transcribe_options)
            
            if self.cancel_requested:
                return
            
            if progress_callback:
                elapsed_time = time.time() - self.start_time
                progress_callback(90, f"Finalizando transcrição... Tempo decorrido: {format_time(elapsed_time)}")
            
            # Extrair texto
            transcribed_text = result.get('text', '')
            
            # Calcular tempo total
            total_time = time.time() - self.start_time
            
            if completion_callback:
                completion_callback(transcribed_text)
        
        except Exception as e:
            if error_callback:
                error_callback(f"Erro na transcrição: {str(e)}")
        
        finally:
            self.is_transcribing = False
    
    def cancel(self):
        """
        Cancela a transcrição em andamento.
        """
        if self.is_transcribing:
            self.cancel_requested = True
            return True
        return False

def format_time(seconds):
    """
    Formata o tempo em segundos para uma string legível.
    
    Args:
        seconds (float): Tempo em segundos
        
    Returns:
        str: Tempo formatado
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}min {seconds}s"
    elif minutes > 0:
        return f"{minutes}min {seconds}s"
    else:
        return f"{seconds}s"
