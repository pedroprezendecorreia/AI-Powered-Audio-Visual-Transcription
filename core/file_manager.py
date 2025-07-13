"""
Módulo de gerenciamento de arquivos para o aplicativo de transcrição.
"""
import os
import shutil
from pathlib import Path

class FileManager:
    """
    Classe para gerenciamento de operações de arquivo.
    """
    @staticmethod
    def is_valid_media_file(file_path):
        """
        Verifica se o arquivo é um arquivo de mídia válido.
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            bool: True se for um arquivo de mídia válido, False caso contrário
        """
        if not os.path.isfile(file_path):
            return False
        
        valid_extensions = [
            '.mp3', '.mp4', '.wav', '.ogg', '.flac', 
            '.avi', '.mov', '.mkv', '.webm', '.m4a'
        ]
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in valid_extensions
    
    @staticmethod
    def is_youtube_url(url):
        """
        Verifica se a URL é uma URL do YouTube válida.
        
        Args:
            url (str): URL a ser verificada
            
        Returns:
            bool: True se for uma URL do YouTube válida, False caso contrário
        """
        youtube_domains = [
            'youtube.com', 'www.youtube.com', 
            'youtu.be', 'www.youtu.be',
            'm.youtube.com'
        ]
        
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            return any(domain in parsed_url.netloc for domain in youtube_domains)
        except:
            return False
    
    @staticmethod
    def get_default_save_directory():
        """
        Retorna o diretório padrão para salvar arquivos.
        
        Returns:
            str: Caminho do diretório padrão
        """
        return str(Path.home() / "Downloads")
    
    @staticmethod
    def ensure_directory_exists(directory):
        """
        Garante que o diretório exista, criando-o se necessário.
        
        Args:
            directory (str): Caminho do diretório
            
        Returns:
            bool: True se o diretório existir ou for criado com sucesso, False caso contrário
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_name(file_path):
        """
        Retorna o nome do arquivo sem o caminho e a extensão.
        
        Args:
            file_path (str): Caminho completo do arquivo
            
        Returns:
            str: Nome do arquivo sem extensão
        """
        return os.path.splitext(os.path.basename(file_path))[0]
    
    @staticmethod
    def save_text_file(text, file_path):
        """
        Salva texto em um arquivo.
        
        Args:
            text (str): Texto a ser salvo
            file_path (str): Caminho do arquivo
            
        Returns:
            bool: True se o arquivo for salvo com sucesso, False caso contrário
        """
        try:
            # Garantir que o diretório exista
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Salvar o arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def find_media_files_in_folder(folder_path):
        """
        Encontra todos os arquivos de mídia em uma pasta.
        
        Args:
            folder_path (str): Caminho da pasta
            
        Returns:
            list: Lista de caminhos de arquivos de mídia
        """
        if not os.path.isdir(folder_path):
            return []
        
        media_extensions = [
            '.mp3', '.mp4', '.wav', '.ogg', '.flac', 
            '.avi', '.mov', '.mkv', '.webm', '.m4a'
        ]
        
        media_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in media_extensions):
                    media_files.append(os.path.join(root, file))
        
        return media_files
