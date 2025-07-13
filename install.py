"""
Script de instalação para o Whisper Transcriber.

Este script instala todas as dependências necessárias para o aplicativo,
verifica a presença do FFmpeg e configura o ambiente.
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
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_step(text):
    """Imprime um passo da instalação."""
    print(f"\n>> {text}")

def run_command(command, check=True):
    """Executa um comando e retorna o resultado."""
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
        print(f"Erro ao executar comando: {e}")
        return None

def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print_step("Verificando versão do Python")
    
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Versão do Python incompatível: {major}.{minor}")
        print("O Whisper Transcriber requer Python 3.8 ou superior.")
        return False
    
    print(f"Versão do Python: {major}.{minor} (OK)")
    return True

def install_pip_dependencies():
    """Instala as dependências via pip."""
    print_step("Instalando dependências via pip")
    
    # Instalar dependências básicas
    basic_dependencies = [
        "PySide6",
        "openai-whisper",
        "yt-dlp"
    ]
    
    for dep in basic_dependencies:
        print(f"Instalando {dep}...")
        result = run_command([sys.executable, "-m", "pip", "install", dep])
        if result and result.returncode == 0:
            print(f"{dep} instalado com sucesso.")
        else:
            print(f"Erro ao instalar {dep}. Por favor, instale manualmente: pip install {dep}")
    
    # Instalar PyTorch separadamente
    print_step("Instalando PyTorch")
    
    # Instalar cada componente do PyTorch separadamente
    torch_components = ["torch", "torchvision", "torchaudio"]
    
    for component in torch_components:
        print(f"Instalando {component}...")
        result = run_command([sys.executable, "-m", "pip", "install", component], check=False)
        if result and result.returncode == 0:
            print(f"{component} instalado com sucesso.")
        else:
            print(f"Aviso: Não foi possível instalar {component} automaticamente.")
            print(f"Por favor, instale manualmente: pip install {component}")
            
            # Para o torch, oferecer instruções adicionais
            if component == "torch":
                print("\nPara instalar o PyTorch manualmente:")
                print("1. Visite https://pytorch.org/get-started/locally/")
                print("2. Selecione suas preferências e copie o comando de instalação")
                print("3. Execute o comando no prompt de comando")

def check_ffmpeg():
    """Verifica se o FFmpeg está instalado e, se não, tenta instalá-lo."""
    print_step("Verificando FFmpeg")
    
    # Verificar se o FFmpeg já está instalado
    result = run_command(["ffmpeg", "-version"], check=False)
    if result and result.returncode == 0:
        print("FFmpeg já está instalado.")
        return True
    
    print("FFmpeg não encontrado. Tentando instalar...")
    
    if platform.system() == "Windows":
        return install_ffmpeg_windows()
    else:
        print("Instalação automática do FFmpeg só é suportada no Windows.")
        print("Por favor, instale o FFmpeg manualmente:")
        print("1. Baixe em https://ffmpeg.org/download.html")
        print("2. Extraia o arquivo e adicione a pasta 'bin' ao PATH do sistema")
        return False

def install_ffmpeg_windows():
    """Instala o FFmpeg no Windows."""
    try:
        # URL do FFmpeg para Windows (versão estática)
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        # Diretório de instalação
        install_dir = os.path.join(os.path.expanduser("~"), "ffmpeg")
        os.makedirs(install_dir, exist_ok=True)
        
        # Baixar o arquivo
        print("Baixando FFmpeg...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            temp_path = temp_file.name
            urllib.request.urlretrieve(ffmpeg_url, temp_path)
        
        # Extrair o arquivo
        print("Extraindo FFmpeg...")
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        
        # Encontrar a pasta bin
        ffmpeg_bin = None
        for root, dirs, files in os.walk(install_dir):
            if "bin" in dirs:
                ffmpeg_bin = os.path.join(root, "bin")
                break
        
        if not ffmpeg_bin:
            print("Não foi possível encontrar a pasta 'bin' do FFmpeg.")
            return False
        
        # Adicionar ao PATH
        print("Adicionando FFmpeg ao PATH...")
        
        # Adicionar ao PATH da sessão atual
        os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
        
        # Instruções para adicionar permanentemente ao PATH
        print("\nPara adicionar o FFmpeg permanentemente ao PATH:")
        print(f"1. Adicione o seguinte caminho às variáveis de ambiente: {ffmpeg_bin}")
        print("2. Reinicie o prompt de comando após a alteração")
        
        # Verificar se a instalação funcionou
        result = run_command(["ffmpeg", "-version"], check=False)
        if result and result.returncode == 0:
            print("FFmpeg instalado com sucesso.")
            return True
        else:
            print("FFmpeg instalado, mas não está no PATH.")
            return False
    
    except Exception as e:
        print(f"Erro ao instalar FFmpeg: {e}")
        return False
    finally:
        # Limpar arquivo temporário
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass

def check_cuda():
    """Verifica se o CUDA está disponível."""
    print_step("Verificando suporte a CUDA")
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
            
            print(f"CUDA está disponível: {cuda_available}")
            print(f"Dispositivos CUDA: {device_count}")
            print(f"GPU: {device_name}")
        else:
            print("CUDA não está disponível.")
            print("O aplicativo usará a CPU para processamento por padrão.")
            print("Para habilitar o processamento por GPU:")
            print("1. Instale os drivers mais recentes da NVIDIA")
            print("2. Instale o CUDA Toolkit compatível com sua versão do PyTorch")
    
    except ImportError:
        print("Não foi possível verificar o suporte a CUDA.")
        print("Verifique se o PyTorch está instalado corretamente.")

def create_shortcut_windows():
    """Cria um atalho para o aplicativo no Windows."""
    print_step("Criando atalho para o aplicativo")
    
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
        
        print(f"Atalho criado em: {path}")
    except ImportError:
        print("Não foi possível criar o atalho.")
        print("Para iniciar o aplicativo, execute: python main.py")
    except Exception as e:
        print(f"Erro ao criar atalho: {e}")
        print("Para iniciar o aplicativo, execute: python main.py")

def main():
    """Função principal do script de instalação."""
    print_header("Instalação do Whisper Transcriber")
    
    # Verificar sistema operacional
    if platform.system() != "Windows":
        print("AVISO: Este aplicativo foi projetado para Windows.")
        print("A instalação pode prosseguir, mas a compatibilidade não é garantida.")
    
    # Verificar versão do Python
    if not check_python_version():
        return
    
    # Instalar dependências
    install_pip_dependencies()
    
    # Verificar FFmpeg
    check_ffmpeg()
    
    # Verificar CUDA
    check_cuda()
    
    # Criar atalho (apenas Windows)
    if platform.system() == "Windows":
        try:
            run_command([sys.executable, "-m", "pip", "install", "pywin32", "winshell"], check=False)
            create_shortcut_windows()
        except:
            pass
    
    print_header("Instalação Concluída")
    print("O Whisper Transcriber foi instalado com sucesso!")
    print("Para iniciar o aplicativo, execute: python main.py")

if __name__ == "__main__":
    main()
