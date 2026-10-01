import os

class ConfigManager:
    def __init__(self, server_dir: str):
        self.server_dir = server_dir

    def ensure_server_dir(self) -> None:
        os.makedirs(self.server_dir, exist_ok=True)
        os.makedirs(os.path.join(self.server_dir, 'mods'), exist_ok=True)

    def accept_eula(self) -> None:
        self.ensure_server_dir()
        eula_path = os.path.join(self.server_dir, 'eula.txt')
        with open(eula_path, 'w', encoding='utf-8') as f:
            f.write('eula=true\n')

    def write_server_properties(self, properties: dict) -> None:
        self.ensure_server_dir()
        default_props = {
            'online-mode': 'false',
            'server-port': '25565',
            'motd': 'MCServerManager - Servidor No Premium',
            'max-players': '20',
            'difficulty': 'normal',
            'gamemode': 'survival',
            'enable-command-block': 'true',
            'spawn-protection': '0',
            'view-distance': '10'
        }
        default_props.update(properties)
        
        props_path = os.path.join(self.server_dir, 'server.properties')
        with open(props_path, 'w', encoding='utf-8') as f:
            for k, v in default_props.items():
                f.write(f'{k}={v}\n')

    def read_server_properties(self) -> dict:
        props_path = os.path.join(self.server_dir, 'server.properties')
        props = {}
        if os.path.exists(props_path):
            with open(props_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        props[key] = val
        return props

    def get_server_dir(self) -> str:
        return self.server_dir

    def setup_no_premium(self) -> None:
        self.accept_eula()
        self.write_server_properties({'online-mode': 'false'})
