import os
import sys
import subprocess
import threading
from typing import Callable, Optional

class ServerProcess:
    def __init__(self, server_dir: str, jar_name: str = 'server.jar', ram_min: str = '1G', ram_max: str = '4G', java_path: str = 'java'):
        self.server_dir = server_dir
        self.jar_name = jar_name
        self.ram_min = ram_min
        self.ram_max = ram_max
        self.java_path = java_path
        
        self._process: Optional[subprocess.Popen] = None
        self._running: bool = False
        self._output_thread: Optional[threading.Thread] = None
        self._on_output: Optional[Callable[[str], None]] = None
        self._on_stopped: Optional[Callable[[], None]] = None

    def start(self, on_output: Callable[[str], None], on_stopped: Callable[[], None]) -> bool:
        if self.is_running:
            return False
            
        self._on_output = on_output
        self._on_stopped = on_stopped
        
        # Detectar si es un servidor Forge moderno (1.17+) con win_args.txt / unix_args.txt
        args_file = None
        target_args_name = 'win_args.txt' if sys.platform == 'win32' else 'unix_args.txt'
        for root, _, files in os.walk(self.server_dir):
            if target_args_name in files:
                args_file = os.path.relpath(os.path.join(root, target_args_name), self.server_dir)
                break

        if args_file:
            cmd = [self.java_path, f'-Xms{self.ram_min}', f'-Xmx{self.ram_max}', f'@{args_file}', 'nogui']
        else:
            # Buscar server.jar o cualquier forge-*.jar
            target_jar = self.jar_name
            if not os.path.isfile(os.path.join(self.server_dir, target_jar)):
                for f in os.listdir(self.server_dir):
                    if f.startswith('forge-') and f.endswith('.jar'):
                        target_jar = f
                        break
            cmd = [self.java_path, f'-Xms{self.ram_min}', f'-Xmx{self.ram_max}', '-jar', target_jar, 'nogui']
        
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            
            self._process = subprocess.Popen(
                cmd,
                cwd=self.server_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags
            )
            
            self._running = True
            self._output_thread = threading.Thread(target=self._read_output, daemon=True)
            self._output_thread.start()
            
            return True
        except Exception as e:
            if self._on_output:
                self._on_output(f"Error starting server: {e}")
            return False

    def stop(self) -> bool:
        if not self.is_running or not self._process or not self._process.stdin:
            return False
            
        try:
            self._process.stdin.write('stop\n')
            self._process.stdin.flush()
            return True
        except Exception:
            return False

    def send_command(self, command: str) -> None:
        if self.is_running and self._process and self._process.stdin:
            try:
                self._process.stdin.write(command + '\n')
                self._process.stdin.flush()
            except Exception:
                pass

    def kill(self) -> None:
        if self._process:
            self._process.kill()

    @property
    def is_running(self) -> bool:
        return self._running

    def _read_output(self) -> None:
        if not self._process or not self._process.stdout:
            return
            
        for line in iter(self._process.stdout.readline, ''):
            if self._on_output:
                self._on_output(line.rstrip('\n'))
                
        self._process.wait()
        self._running = False
        
        if self._on_stopped:
            self._on_stopped()
