"""
Installation script for Whisper Transcriber.

Installs the Python dependencies (PySide6 + faster-whisper). faster-whisper
bundles its own audio decoder, so there is no separate FFmpeg or PyTorch step.
"""
import os
import sys
import subprocess
import platform


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_step(text):
    print(f"\n>> {text}")


def check_python_version():
    print_step("Checking Python version")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Incompatible Python version: {major}.{minor}")
        print("Whisper Transcriber requires Python 3.8 or higher.")
        return False
    print(f"Python version: {major}.{minor} (OK)")
    return True


def install_dependencies():
    print_step("Installing dependencies")
    requirements = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-r", requirements]
    )
    if result.returncode == 0:
        print("Dependencies installed successfully.")
        return True
    print("Error installing dependencies. Try manually: pip install -r requirements.txt")
    return False


def create_shortcut_windows():
    print_step("Creating application shortcut")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pywin32", "winshell"],
            check=False,
        )
        import winshell
        from win32com.client import Dispatch

        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(winshell.desktop(), "Whisper Transcriber.lnk")

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = os.path.join(here, "main.py")
        shortcut.WorkingDirectory = here
        shortcut.save()
        print(f"Shortcut created at: {path}")
    except Exception as e:
        print(f"Could not create shortcut ({e}). To start the app, run: python main.py")


def main():
    print_header("Whisper Transcriber Installation")

    if not check_python_version():
        return

    if not install_dependencies():
        return

    if platform.system() == "Windows":
        create_shortcut_windows()

    print_header("Installation Complete")
    print("To start the application, run: python main.py")


if __name__ == "__main__":
    main()
