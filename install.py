"""
Installation script for Whisper Transcriber.

This script installs all necessary dependencies for the application,
checks for FFmpeg presence, and configures the environment.
"""
import os
import sys
import subprocess
import platform
import site
import shutil
from pathlib import Path
import tempfile
import urllib.request
import zipfile

def print_header(text):
    """Prints a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_step(text):
    """Prints an installation step."""
    print(f"\n>> {text}")

def run_command(command, check=True):
    """Executes a command and returns the result."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None

def check_python_version():
    """Checks if the Python version is compatible."""
    print_step("Checking Python version")
    
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Incompatible Python version: {major}.{minor}")
        print("Whisper Transcriber requires Python 3.8 or higher.")
        return False
    
    print(f"Python version: {major}.{minor} (OK)")
    return True

def install_pip_dependencies():
    """Installs dependencies via pip."""
    print_step("Installing pip dependencies")
    
    # Install basic dependencies
    basic_dependencies = [
        "PySide6",
        "openai-whisper",
        "yt-dlp"
    ]
    
    for dep in basic_dependencies:
        print(f"Installing {dep}...")
        result = run_command([sys.executable, "-m", "pip", "install", dep])
        if result and result.returncode == 0:
            print(f"{dep} installed successfully.")
        else:
            print(f"Error installing {dep}. Please install manually: pip install {dep}")
    
    # Install PyTorch separately
    print_step("Installing PyTorch")
    
    # Install each PyTorch component separately
    torch_components = ["torch", "torchvision", "torchaudio"]
    
    for component in torch_components:
        print(f"Installing {component}...")
        result = run_command([sys.executable, "-m", "pip", "install", component], check=False)
        if result and result.returncode == 0:
            print(f"{component} installed successfully.")
        else:
            print(f"Warning: Could not install {component} automatically.")
            print(f"Please install manually: pip install {component}")
            
            # For torch, provide additional instructions
            if component == "torch":
                print("\nTo install PyTorch manually:")
                print("1. Visit https://pytorch.org/get-started/locally/")
                print("2. Select your preferences and copy the installation command")
                print("3. Execute the command in your command prompt")

def check_ffmpeg():
    """Checks if FFmpeg is installed and attempts to install it if not."""
    print_step("Checking FFmpeg")
    
    # Check if FFmpeg is already installed
    result = run_command(["ffmpeg", "-version"], check=False)
    if result and result.returncode == 0:
        print("FFmpeg is already installed.")
        return True
    
    print("FFmpeg not found. Attempting to install...")
    
    if platform.system() == "Windows":
        return install_ffmpeg_windows()
    else:
        print("Automatic FFmpeg installation is only supported on Windows.")
        print("Please install FFmpeg manually:")
        print("1. Download from https://ffmpeg.org/download.html")
        print("2. Extract the archive and add the 'bin' folder to your system's PATH")
        return False

def install_ffmpeg_windows():
    """Installs FFmpeg on Windows."""
    try:
        # FFmpeg URL for Windows (static version)
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        # Installation directory
        install_dir = os.path.join(os.path.expanduser("~"), "ffmpeg")
        os.makedirs(install_dir, exist_ok=True)
        
        # Download the file
        print("Downloading FFmpeg...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            temp_path = temp_file.name
            urllib.request.urlretrieve(ffmpeg_url, temp_path)
        
        # Extract the file
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        
        # Find the bin folder
        ffmpeg_bin = None
        for root, dirs, files in os.walk(install_dir):
            if "bin" in dirs:
                ffmpeg_bin = os.path.join(root, "bin")
                break
        
        if not ffmpeg_bin:
            print("Could not find the 'bin' folder for FFmpeg.")
            return False
        
        # Add to PATH
        print("Adding FFmpeg to PATH...")
        
        # Add to current session's PATH
        os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
        
        # Instructions to permanently add to PATH
        print("\nTo permanently add FFmpeg to your PATH:")
        print(f"1. Add the following path to your environment variables: {ffmpeg_bin}")
        print("2. Restart your command prompt after the change")
        
        # Verify if installation worked
        result = run_command(["ffmpeg", "-version"], check=False)
        if result and result.returncode == 0:
            print("FFmpeg installed successfully.")
            return True
        else:
            print("FFmpeg installed, but not in PATH.")
            return False
    
    except Exception as e:
        print(f"Error installing FFmpeg: {e}")
        return False
    finally:
        # Clean up temporary file
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass

def check_cuda():
    """Checks if CUDA is available."""
    print_step("Checking CUDA support")
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
            
            print(f"CUDA is available: {cuda_available}")
            print(f"CUDA Devices: {device_count}")
            print(f"GPU: {device_name}")
        else:
            print("CUDA is not available.")
            print("The application will use CPU for processing by default.")
            print("To enable GPU processing:")
            print("1. Install the latest NVIDIA drivers")
            print("2. Install the CUDA Toolkit compatible with your PyTorch version")
    
    except ImportError:
        print("Could not check CUDA support.")
        print("Please ensure PyTorch is installed correctly.")

def create_shortcut_windows():
    """Creates a shortcut for the application on Windows."""
    print_step("Creating application shortcut")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Whisper Transcriber.lnk")
        
        target = os.path.abspath("main.py")
        wDir = os.path.abspath(".")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = target
        shortcut.WorkingDirectory = wDir
        shortcut.save()
        
        print(f"Shortcut created at: {path}")
    except ImportError:
        print("Could not create shortcut.")
        print("To start the application, run: python main.py")
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        print("To start the application, run: python main.py")

def main():
    """Main function of the installation script."""
    print_header("Whisper Transcriber Installation")
    
    # Check operating system
    if platform.system() != "Windows":
        print("WARNING: This application was designed for Windows.")
        print("Installation may proceed, but compatibility is not guaranteed.")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    install_pip_dependencies()
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Check CUDA
    check_cuda()
    
    # Create shortcut (Windows only)
    if platform.system() == "Windows":
        try:
            run_command([sys.executable, "-m", "pip", "install", "pywin32", "winshell"], check=False)
            create_shortcut_windows()
        except:
            pass
    
    print_header("Installation Complete")
    print("Whisper Transcriber installed successfully!")
    print("To start the application, run: python main.py")

if __name__ == "__main__":
    main()


