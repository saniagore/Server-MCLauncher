import subprocess
import threading
import socket
import requests
from typing import Optional, Callable

class ConnectivityManager:
    def __init__(self):
        self._tunnel_process: Optional[subprocess.Popen] = None
        self._tunnel_type: Optional[str] = None
        self._tunnel_thread: Optional[threading.Thread] = None

    def check_playit_installed(self) -> bool:
        try:
            subprocess.run(['playit', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except FileNotFoundError:
            return False

    def check_ngrok_installed(self) -> bool:
        try:
            subprocess.run(['ngrok', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except FileNotFoundError:
            return False

    def _read_tunnel_output(self, on_output: Callable[[str], None]) -> None:
        if not self._tunnel_process or not self._tunnel_process.stdout:
            return
        for line in iter(self._tunnel_process.stdout.readline, ''):
            if line:
                on_output(line.rstrip('\n'))
        self._tunnel_process.wait()

    def start_playit_tunnel(self, port: int = 25565, on_output: Optional[Callable[[str], None]] = None) -> bool:
        if self.is_tunnel_running:
            return False
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            self._tunnel_process = subprocess.Popen(
                ['playit'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags
            )
            self._tunnel_type = 'playit'
            if on_output:
                self._tunnel_thread = threading.Thread(target=self._read_tunnel_output, args=(on_output,), daemon=True)
                self._tunnel_thread.start()
            return True
        except Exception:
            return False

    def start_ngrok_tunnel(self, port: int = 25565, on_output: Optional[Callable[[str], None]] = None) -> bool:
        if self.is_tunnel_running:
            return False
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            self._tunnel_process = subprocess.Popen(
                ['ngrok', 'tcp', str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags
            )
            self._tunnel_type = 'ngrok'
            if on_output:
                self._tunnel_thread = threading.Thread(target=self._read_tunnel_output, args=(on_output,), daemon=True)
                self._tunnel_thread.start()
            return True
        except Exception:
            return False

    def stop_tunnel(self) -> None:
        if self._tunnel_process:
            self._tunnel_process.kill()
            self._tunnel_process = None
        self._tunnel_type = None

    @property
    def is_tunnel_running(self) -> bool:
        return self._tunnel_process is not None and self._tunnel_process.poll() is None

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

def get_public_ip() -> str:
    try:
        resp = requests.get('https://api.ipify.org', timeout=5)
        resp.raise_for_status()
        return resp.text.strip()
    except Exception:
        return "Desconocida"
