"""
File management module for the transcription application.
"""
import os
import shutil
from pathlib import Path

class FileManager:
    """
    Class for managing file operations.
    """
    @staticmethod
    def is_valid_media_file(file_path):
        """
        Checks if the file is a valid media file.
        
        Args:
            file_path (str): File path
            
        Returns:
            bool: True if it's a valid media file, False otherwise
        """
        if not os.path.isfile(file_path):
            return False
        
        valid_extensions = [
            ".mp3", ".mp4", ".wav", ".ogg", ".flac", 
            ".avi", ".mov", ".mkv", ".webm", ".m4a"
        ]
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in valid_extensions
    
    @staticmethod
    def is_youtube_url(url):
        """
        Checks if the URL is a valid YouTube URL.
        
        Args:
            url (str): URL to be checked
            
        Returns:
            bool: True if it's a valid YouTube URL, False otherwise
        """
        youtube_domains = [
            "youtube.com", "www.youtube.com", 
            "youtu.be", "www.youtu.be",
            "m.youtube.com"
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
        Returns the default directory for saving files.
        
        Returns:
            str: Path to the default directory
        """
        return str(Path.home() / "Downloads")
    
    @staticmethod
    def ensure_directory_exists(directory):
        """
        Ensures that the directory exists, creating it if necessary.
        
        Args:
            directory (str): Directory path
            
        Returns:
            bool: True if the directory exists or is created successfully, False otherwise
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_name(file_path):
        """
        Returns the file name without path and extension.
        
        Args:
            file_path (str): Full file path
            
        Returns:
            str: File name without extension
        """
        return os.path.splitext(os.path.basename(file_path))[0]
    
    @staticmethod
    def save_text_file(text, file_path):
        """
        Saves text to a file.
        
        Args:
            text (str): Text to be saved
            file_path (str): File path
            
        Returns:
            bool: True if the file is saved successfully, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def find_media_files_in_folder(folder_path):
        """
        Finds all media files in a folder.
        
        Args:
            folder_path (str): Folder path
            
        Returns:
            list: List of media file paths
        """
        if not os.path.isdir(folder_path):
            return []
        
        media_extensions = [
            ".mp3", ".mp4", ".wav", ".ogg", ".flac", 
            ".avi", ".mov", ".mkv", ".webm", ".m4a"
        ]
        
        media_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in media_extensions):
                    media_files.append(os.path.join(root, file))
        
        return media_files


