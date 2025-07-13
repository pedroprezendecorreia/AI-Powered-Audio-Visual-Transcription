"""
Módulo de backend para download de vídeos do YouTube.
"""
import os
import subprocess
import threading
from pathlib import Path

class YouTubeDownloader:
    """
    Classe para download de vídeos do YouTube usando yt-dlp.
    """
    def __init__(self):
        self.download_thread = None
        self.is_downloading = False
        self.current_process = None
        self.download_path = str(Path.home() / "Downloads")
    
    def download(self, url, progress_callback=None, completion_callback=None, error_callback=None):
        """
        Inicia o download de um vídeo do YouTube.
        
        Args:
            url (str): URL do vídeo do YouTube
            progress_callback (callable): Função de callback para atualização de progresso
            completion_callback (callable): Função de callback para conclusão do download
            error_callback (callable): Função de callback para erros
        """
        if self.is_downloading:
            if error_callback:
                error_callback("Já existe um download em andamento.")
            return
        
        self.is_downloading = True
        
        # Iniciar thread de download
        self.download_thread = threading.Thread(
            target=self._download_thread,
            args=(url, progress_callback, completion_callback, error_callback)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def _download_thread(self, url, progress_callback, completion_callback, error_callback):
        """
        Thread de download.
        
        Args:
            url (str): URL do vídeo do YouTube
            progress_callback (callable): Função de callback para atualização de progresso
            completion_callback (callable): Função de callback para conclusão do download
            error_callback (callable): Função de callback para erros
        """
        try:
            # Criar diretório de downloads se não existir
            os.makedirs(self.download_path, exist_ok=True)
            
            # Comando para download apenas do áudio (formato mp3)
            cmd = [
                "yt-dlp",
                "-f", "bestaudio",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "--newline",
                "--progress",
                "-o", f"{self.download_path}/%(title)s.%(ext)s",
                url
            ]
            
            # Iniciar processo
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitorar saída para atualização de progresso
            output_file = None
            for line in self.current_process.stdout:
                if "[download]" in line and "%" in line:
                    try:
                        # Extrair porcentagem de progresso
                        percent_str = line.split("%")[0].split()[-1]
                        percent = float(percent_str)
                        if progress_callback:
                            progress_callback(int(percent))
                    except (ValueError, IndexError):
                        pass
                
                # Capturar nome do arquivo de saída
                if "Destination:" in line:
                    try:
                        output_file = line.split("Destination: ")[1].strip()
                    except (IndexError, AttributeError):
                        pass
            
            # Verificar código de retorno
            return_code = self.current_process.wait()
            
            if return_code == 0:
                if completion_callback:
                    completion_callback(output_file)
            else:
                error_message = self.current_process.stderr.read()
                if error_callback:
                    error_callback(f"Erro no download: {error_message}")
        
        except Exception as e:
            if error_callback:
                error_callback(f"Erro: {str(e)}")
        
        finally:
            self.is_downloading = False
            self.current_process = None
    
    def cancel(self):
        """
        Cancela o download em andamento.
        """
        if self.is_downloading and self.current_process:
            try:
                self.current_process.terminate()
                self.current_process = None
                self.is_downloading = False
                return True
            except Exception:
                return False
        return False
