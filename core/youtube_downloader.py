"""
Backend module for downloading YouTube videos.
"""
import os
import subprocess
import threading
from pathlib import Path

class YouTubeDownloader:
    """
    Class for downloading YouTube videos using yt-dlp.
    """
    def __init__(self):
        self.download_thread = None
        self.is_downloading = False
        self.current_process = None
        self.download_path = str(Path.home() / "Downloads")
    
    def download(self, url, progress_callback=None, completion_callback=None, error_callback=None):
        """
        Starts downloading a YouTube video.
        
        Args:
            url (str): YouTube video URL
            progress_callback (callable): Callback function for progress updates
            completion_callback (callable): Callback function for download completion
            error_callback (callable): Callback function for errors
        """
        if self.is_downloading:
            if error_callback:
                error_callback("A download is already in progress.")
            return
        
        self.is_downloading = True
        
        # Start download thread
        self.download_thread = threading.Thread(
            target=self._download_thread,
            args=(url, progress_callback, completion_callback, error_callback)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def _download_thread(self, url, progress_callback, completion_callback, error_callback):
        """
        Download thread.
        
        Args:
            url (str): YouTube video URL
            progress_callback (callable): Callback function for progress updates
            completion_callback (callable): Callback function for download completion
            error_callback (callable): Callback function for errors
        """
        try:
            # Create downloads directory if it doesn't exist
            os.makedirs(self.download_path, exist_ok=True)
            
            # Command to download only audio (mp3 format)
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
            
            # Start process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor output for progress updates
            output_file = None
            for line in self.current_process.stdout:
                if "[download]" in line and "%" in line:
                    try:
                        # Extract percentage progress
                        percent_str = line.split("%")[0].split()[-1]
                        percent = float(percent_str)
                        if progress_callback:
                            progress_callback(int(percent))
                    except (ValueError, IndexError):
                        pass
                
                # Capture output file name
                if "Destination:" in line:
                    try:
                        output_file = line.split("Destination: ")[1].strip()
                    except (IndexError, AttributeError):
                        pass
            
            # Check return code
            return_code = self.current_process.wait()
            
            if return_code == 0:
                if completion_callback:
                    completion_callback(output_file)
            else:
                error_message = self.current_process.stderr.read()
                if error_callback:
                    error_callback(f"Download error: {error_message}")
        
        except Exception as e:
            if error_callback:
                error_callback(f"Error: {str(e)}")
        
        finally:
            self.is_downloading = False
            self.current_process = None
    
    def cancel(self):
        """
        Cancels the ongoing download.
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


