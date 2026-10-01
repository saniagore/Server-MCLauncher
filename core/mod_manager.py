import os
import shutil
import subprocess
import sys

class ModManager:
    def __init__(self, server_dir: str):
        self.server_dir = server_dir

    @property
    def mods_dir(self) -> str:
        return os.path.join(self.server_dir, 'mods')

    def ensure_mods_dir(self) -> None:
        os.makedirs(self.mods_dir, exist_ok=True)

    def list_mods(self) -> list[dict]:
        self.ensure_mods_dir()
        mods = []
        for f in os.listdir(self.mods_dir):
            if f.endswith('.jar'):
                path = os.path.join(self.mods_dir, f)
                size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)
                mods.append({
                    'name': f,
                    'path': path,
                    'size_mb': size_mb
                })
        return mods

    def add_mod(self, source_path: str) -> bool:
        self.ensure_mods_dir()
        if not os.path.isfile(source_path) or not source_path.endswith('.jar'):
            return False
        try:
            filename = os.path.basename(source_path)
            dest_path = os.path.join(self.mods_dir, filename)
            shutil.copy2(source_path, dest_path)
            return True
        except Exception:
            return False

    def remove_mod(self, mod_name: str) -> bool:
        self.ensure_mods_dir()
        path = os.path.join(self.mods_dir, mod_name)
        if os.path.isfile(path):
            try:
                os.remove(path)
                return True
            except Exception:
                return False
        return False

    def add_mods_from_list(self, paths: list[str]) -> tuple[int, int]:
        success = 0
        fail = 0
        for p in paths:
            if self.add_mod(p):
                success += 1
            else:
                fail += 1
        return success, fail

    def open_mods_folder(self) -> None:
        self.ensure_mods_dir()
        if sys.platform == 'win32':
            os.startfile(self.mods_dir)
        elif sys.platform == 'darwin':
            subprocess.run(['open', self.mods_dir])
        else:
            subprocess.run(['xdg-open', self.mods_dir])
