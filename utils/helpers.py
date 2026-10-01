import os
import subprocess
import socket
import re
from typing import Optional

def find_java() -> Optional[str]:
    try:
        subprocess.run(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'java'
    except FileNotFoundError:
        pass
    
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        java_exe = os.path.join(java_home, 'bin', 'java.exe' if os.name == 'nt' else 'java')
        if os.path.exists(java_exe):
            return java_exe
            
    if os.name == 'nt':
        program_files = [os.environ.get('ProgramFiles', 'C:\\Program Files'), os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')]
        for pf in program_files:
            java_dir = os.path.join(pf, 'Java')
            if os.path.exists(java_dir):
                for folder in os.listdir(java_dir):
                    bin_path = os.path.join(java_dir, folder, 'bin', 'java.exe')
                    if os.path.exists(bin_path):
                        return bin_path
    return None

def get_java_version(java_path: str = 'java') -> Optional[str]:
    try:
        result = subprocess.run([java_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        match = re.search(r'version "([^"]+)"', result.stdout)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None

def format_bytes(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0

def get_servers_base_dir() -> str:
    base = os.path.join(os.getcwd(), 'servers')
    os.makedirs(base, exist_ok=True)
    return base

def sanitize_server_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()
