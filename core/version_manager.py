import os
import re
import subprocess
import requests
from typing import Callable, Optional, List

class VersionManager:
    VANILLA_MANIFEST_URL = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
    PAPER_API_URL = 'https://fill.papermc.io/v3/projects/paper'
    FABRIC_API_URL = 'https://meta.fabricmc.net/v2'
    FORGE_PROMOTIONS_URL = 'https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json'

    @classmethod
    def get_vanilla_versions(cls) -> List[str]:
        try:
            resp = requests.get(cls.VANILLA_MANIFEST_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return [v['id'] for v in data.get('versions', []) if v.get('type') == 'release']
        except Exception:
            return ["1.20.4", "1.20.2", "1.20.1", "1.19.4", "1.18.2", "1.16.5"]

    @classmethod
    def get_paper_versions(cls) -> List[str]:
        try:
            resp = requests.get(cls.PAPER_API_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            versions = []
            for group in data.get('versions', {}).values():
                for v in group:
                    if '-rc' not in v and '-pre' not in v:
                        versions.append(v)
            return versions if versions else ["1.20.4", "1.20.2", "1.20.1", "1.19.4", "1.18.2", "1.16.5"]
        except Exception:
            return ["1.20.4", "1.20.2", "1.20.1", "1.19.4", "1.18.2", "1.16.5"]

    @classmethod
    def get_fabric_versions(cls) -> List[str]:
        try:
            resp = requests.get(f"{cls.FABRIC_API_URL}/versions/game", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return [v['version'] for v in data if v.get('stable')]
        except Exception:
            return ["1.20.4", "1.20.2", "1.20.1", "1.19.4", "1.18.2", "1.16.5"]

    @classmethod
    def get_forge_versions(cls) -> List[str]:
        popular = ["1.20.1", "1.20.4", "1.20.2", "1.19.4", "1.19.2", "1.18.2", "1.16.5", "1.12.2"]
        try:
            resp = requests.get(cls.FORGE_PROMOTIONS_URL, timeout=10)
            resp.raise_for_status()
            promos = resp.json().get('promos', {})
            found = set()
            for k in promos.keys():
                v = k.replace('-latest', '').replace('-recommended', '')
                if re.match(r'^\d+\.\d+(\.\d+)?$', v):
                    found.add(v)
            all_sorted = sorted(list(found), key=lambda s: [int(x) for x in s.split('.')], reverse=True)
            res = [v for v in popular if v in all_sorted] + [v for v in all_sorted if v not in popular]
            return res if res else popular
        except Exception:
            return popular

    @classmethod
    def _download_file(cls, url: str, dest_path: str, progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        try:
            resp = requests.get(url, stream=True, timeout=30)
            resp.raise_for_status()
            total_size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded / total_size)
            
            if progress_callback:
                progress_callback(1.0)
            return True
        except Exception:
            return False

    @classmethod
    def download_vanilla(cls, version: str, dest_dir: str, progress_callback: Optional[Callable[[float], None]] = None) -> str:
        try:
            resp = requests.get(cls.VANILLA_MANIFEST_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            version_url = next((v['url'] for v in data.get('versions', []) if v['id'] == version), None)
            if not version_url:
                return ""
            
            resp = requests.get(version_url, timeout=10)
            resp.raise_for_status()
            v_data = resp.json()
            
            server_url = v_data.get('downloads', {}).get('server', {}).get('url')
            if not server_url:
                return ""
            
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, 'server.jar')
            
            if cls._download_file(server_url, dest_path, progress_callback):
                return dest_path
            return ""
        except Exception:
            return ""

    @classmethod
    def download_paper(cls, version: str, dest_dir: str, progress_callback: Optional[Callable[[float], None]] = None) -> str:
        try:
            resp = requests.get(f"{cls.PAPER_API_URL}/versions/{version}/builds/latest", timeout=10)
            resp.raise_for_status()
            b_data = resp.json()
            
            downloads = b_data.get('downloads', {})
            server_default = downloads.get('server:default') or downloads.get('server')
            
            download_url = None
            if server_default and 'url' in server_default:
                download_url = server_default['url']
            elif downloads:
                first_dl = next(iter(downloads.values()), None)
                if first_dl and 'url' in first_dl:
                    download_url = first_dl['url']
            
            if not download_url:
                return ""
            
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, 'server.jar')
            
            if cls._download_file(download_url, dest_path, progress_callback):
                return dest_path
            return ""
        except Exception:
            return ""

    @classmethod
    def download_fabric(cls, version: str, dest_dir: str, progress_callback: Optional[Callable[[float], None]] = None) -> str:
        try:
            inst_resp = requests.get(f"{cls.FABRIC_API_URL}/versions/installer", timeout=10)
            inst_resp.raise_for_status()
            installer_data = inst_resp.json()
            if not installer_data:
                return ""
            installer_version = installer_data[0]['version']
            
            loader_resp = requests.get(f"{cls.FABRIC_API_URL}/versions/loader/{version}", timeout=10)
            loader_resp.raise_for_status()
            loader_data = loader_resp.json()
            if not loader_data:
                return ""
            loader_version = loader_data[0]['loader']['version']
            
            download_url = f"{cls.FABRIC_API_URL}/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
            
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, 'server.jar')
            
            if cls._download_file(download_url, dest_path, progress_callback):
                return dest_path
            return ""
        except Exception:
            return ""

    @classmethod
    def download_forge(cls, version: str, dest_dir: str, progress_callback: Optional[Callable[[float], None]] = None) -> str:
        try:
            resp = requests.get(cls.FORGE_PROMOTIONS_URL, timeout=10)
            resp.raise_for_status()
            promos = resp.json().get('promos', {})
            
            forge_ver = promos.get(f"{version}-recommended") or promos.get(f"{version}-latest")
            if not forge_ver:
                return ""
                
            installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version}-{forge_ver}/forge-{version}-{forge_ver}-installer.jar"
            
            os.makedirs(dest_dir, exist_ok=True)
            installer_path = os.path.join(dest_dir, "forge-installer.jar")
            
            if progress_callback:
                progress_callback(0.2)
                
            # Descargar instalador
            def step_cb(p):
                if progress_callback:
                    progress_callback(0.2 + p * 0.4)
                    
            if not cls._download_file(installer_url, installer_path, step_cb):
                return ""
                
            if progress_callback:
                progress_callback(0.7)
                
            # Ejecutar instalador del servidor automáticamente
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            subprocess.run(
                ["java", "-jar", "forge-installer.jar", "--installServer"],
                cwd=dest_dir,
                capture_output=True,
                creationflags=creationflags
            )
            
            # Limpiar archivos temporales de instalación
            try:
                if os.path.exists(installer_path):
                    os.remove(installer_path)
                log_file = os.path.join(dest_dir, "forge-installer.jar.log")
                if os.path.exists(log_file):
                    os.remove(log_file)
            except Exception:
                pass
                
            if progress_callback:
                progress_callback(1.0)
                
            return dest_dir
        except Exception:
            return ""

    @classmethod
    def download_server(cls, engine: str, version: str, dest_dir: str, progress_callback: Optional[Callable[[float], None]] = None) -> str:
        engine = engine.lower()
        if engine == 'vanilla':
            return cls.download_vanilla(version, dest_dir, progress_callback)
        elif engine == 'paper':
            return cls.download_paper(version, dest_dir, progress_callback)
        elif engine == 'fabric':
            return cls.download_fabric(version, dest_dir, progress_callback)
        elif engine == 'forge':
            return cls.download_forge(version, dest_dir, progress_callback)
        return ""
