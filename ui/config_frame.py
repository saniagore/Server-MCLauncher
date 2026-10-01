import os
import customtkinter as ctk
import threading
from tkinter import filedialog
from utils.helpers import find_java

class ConfigFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self._versions_cache = {}
        
        self.grid_columnconfigure(0, weight=1)
        
        # --- Section: Servidor ---
        self.lbl_server = ctk.CTkLabel(self, text="Servidor", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_server.grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        
        self.frame_server = ctk.CTkFrame(self)
        self.frame_server.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.frame_server.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.frame_server, text="Nombre:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_name = ctk.CTkEntry(self.frame_server)
        self.entry_name.insert(0, "mi-servidor")
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_server, text="Motor:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.opt_engine = ctk.CTkOptionMenu(self.frame_server, values=['Vanilla', 'Paper', 'Fabric', 'Forge'], command=self._on_engine_change)
        self.opt_engine.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_server, text="Versión:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.opt_version = ctk.CTkOptionMenu(self.frame_server, values=["Cargando..."])
        self.opt_version.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        self.btn_download = ctk.CTkButton(self.frame_server, text="Descargar Servidor", command=self._download_server)
        self.btn_download.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.progress_download = ctk.CTkProgressBar(self.frame_server)
        self.progress_download.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.progress_download.set(0)
        self.progress_download.grid_remove() # Hidden by default
        
        self.lbl_download_status = ctk.CTkLabel(self.frame_server, text="", text_color="#2ecc71")
        self.lbl_download_status.grid(row=5, column=0, columnspan=2, pady=(0, 5))
        
        # --- Section: Recursos ---
        self.lbl_resources = ctk.CTkLabel(self, text="Recursos", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_resources.grid(row=2, column=0, sticky="w", pady=(20, 5), padx=10)
        
        self.frame_resources = ctk.CTkFrame(self)
        self.frame_resources.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.frame_resources.grid_columnconfigure(1, weight=1)
        
        self.lbl_ram_min = ctk.CTkLabel(self.frame_resources, text="RAM Mínima: 1024 MB")
        self.lbl_ram_min.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.slider_ram_min = ctk.CTkSlider(self.frame_resources, from_=512, to=8192, number_of_steps=15, command=lambda v: self._update_ram_label(v, self.lbl_ram_min, "RAM Mínima:"))
        self.slider_ram_min.set(1024)
        self.slider_ram_min.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        self.lbl_ram_max = ctk.CTkLabel(self.frame_resources, text="RAM Máxima: 4096 MB")
        self.lbl_ram_max.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.slider_ram_max = ctk.CTkSlider(self.frame_resources, from_=1024, to=16384, number_of_steps=30, command=lambda v: self._update_ram_label(v, self.lbl_ram_max, "RAM Máxima:"))
        self.slider_ram_max.set(4096)
        self.slider_ram_max.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # --- Section: Configuración ---
        self.lbl_config = ctk.CTkLabel(self, text="Configuración del Servidor", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_config.grid(row=4, column=0, sticky="w", pady=(20, 5), padx=10)
        
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=5, column=0, sticky="ew", padx=10, pady=5)
        self.frame_config.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.frame_config, text="Puerto:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_port = ctk.CTkEntry(self.frame_config)
        self.entry_port.insert(0, "25565")
        self.entry_port.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_config, text="MOTD:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_motd = ctk.CTkEntry(self.frame_config)
        self.entry_motd.insert(0, "Servidor No Premium - MCServerManager")
        self.entry_motd.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_config, text="Max Jugadores:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_max_players = ctk.CTkEntry(self.frame_config)
        self.entry_max_players.insert(0, "20")
        self.entry_max_players.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_config, text="Dificultad:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.opt_difficulty = ctk.CTkOptionMenu(self.frame_config, values=['peaceful', 'easy', 'normal', 'hard'])
        self.opt_difficulty.set('easy')
        self.opt_difficulty.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_config, text="Modo de juego:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.opt_gamemode = ctk.CTkOptionMenu(self.frame_config, values=['survival', 'creative', 'adventure', 'spectator'])
        self.opt_gamemode.set('survival')
        self.opt_gamemode.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        
        self.switch_offline = ctk.CTkSwitch(self.frame_config, text="Modo No Premium (online-mode=false)")
        self.switch_offline.select()
        self.switch_offline.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        # --- Section: Java ---
        self.lbl_java = ctk.CTkLabel(self, text="Java", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_java.grid(row=6, column=0, sticky="w", pady=(20, 5), padx=10)
        
        self.frame_java = ctk.CTkFrame(self)
        self.frame_java.grid(row=7, column=0, sticky="ew", padx=10, pady=5)
        self.frame_java.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.frame_java, text="Ruta de Java:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_java = ctk.CTkEntry(self.frame_java)
        self.entry_java.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        self.btn_browse_java = ctk.CTkButton(self.frame_java, text="Buscar", width=60, command=self._browse_java)
        self.btn_browse_java.grid(row=0, column=2, padx=10, pady=5)
        
        self.lbl_java_version = ctk.CTkLabel(self.frame_java, text="Versión: Desconocida", text_color="#3498db")
        self.lbl_java_version.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        self.btn_detect_java = ctk.CTkButton(self.frame_java, text="Detectar Java", command=self._detect_java)
        self.btn_detect_java.grid(row=1, column=2, padx=10, pady=5)

        # --- Bottom ---
        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.grid(row=8, column=0, sticky="ew", pady=20)
        self.frame_bottom.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_save = ctk.CTkButton(self.frame_bottom, text="Guardar Configuración", fg_color="#3498db", hover_color="#2980b9", command=self._save_config)
        self.btn_save.grid(row=0, column=0, padx=10, pady=10)
        
        self.btn_prepare = ctk.CTkButton(self.frame_bottom, text="Crear/Preparar Servidor", fg_color="#2ecc71", hover_color="#27ae60", command=self._prepare_server)
        self.btn_prepare.grid(row=0, column=1, padx=10, pady=10)

        self.lbl_status_feedback = ctk.CTkLabel(self.frame_bottom, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_status_feedback.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Callback opcional para refrescar el sidebar en MainWindow
        self.on_config_changed = None

        # Init calls
        self._on_engine_change(self.opt_engine.get())
        self._detect_java()

    def _update_ram_label(self, value, label, prefix):
        val_int = int(value)
        # Snap to 512 multiples
        val_int = round(val_int / 512) * 512
        label.configure(text=f"{prefix} {val_int} MB")

    def _on_engine_change(self, engine: str):
        self.opt_version.set("Cargando...")
        threading.Thread(target=self._fetch_versions, args=(engine,), daemon=True).start()

    def _fetch_versions(self, engine: str):
        if engine not in self._versions_cache:
            from core.version_manager import VersionManager
            try:
                engine_lower = engine.lower()
                if engine_lower == 'vanilla':
                    versions = VersionManager.get_vanilla_versions()
                elif engine_lower == 'paper':
                    versions = VersionManager.get_paper_versions()
                elif engine_lower == 'fabric':
                    versions = VersionManager.get_fabric_versions()
                elif engine_lower == 'forge':
                    versions = VersionManager.get_forge_versions()
                else:
                    versions = []
                
                if not versions:
                    versions = ["Error al cargar versiones"]
                self._versions_cache[engine] = versions
            except Exception:
                self._versions_cache[engine] = ["Error de conexión"]
            
        def update_ui():
            self.opt_version.configure(values=self._versions_cache[engine])
            self.opt_version.set(self._versions_cache[engine][0])
            
        self.after(0, update_ui)

    def _download_server(self):
        engine = self.opt_engine.get()
        version = self.opt_version.get()
        server_dir = self.get_server_dir()
        
        if version in ("Cargando...", "Error al cargar versiones", "Error de conexión"):
            return
        
        self.progress_download.grid()
        self.progress_download.set(0)
        self.btn_download.configure(state="disabled", text="Descargando...")
        
        def do_download():
            from core.version_manager import VersionManager
            import os
            os.makedirs(server_dir, exist_ok=True)
            
            def progress_cb(value):
                self.after(0, self.progress_download.set, value)
            
            result = VersionManager.download_server(engine, version, server_dir, progress_cb)
            
            def on_done():
                self.btn_download.configure(state="normal", text="Descargar Servidor")
                self.progress_download.grid_remove()
                if result:
                    self.lbl_download_status.configure(
                        text=f"✅ Servidor {engine} {version} descargado exitosamente",
                        text_color="#2ecc71"
                    )
                else:
                    self.lbl_download_status.configure(
                        text=f"❌ Error al descargar {engine} {version}",
                        text_color="#e74c3c"
                    )
                if self.on_config_changed:
                    self.on_config_changed()
            self.after(0, on_done)
        
        threading.Thread(target=do_download, daemon=True).start()

    def _detect_java(self):
        java_path = find_java()
        if java_path:
            self.entry_java.delete(0, 'end')
            self.entry_java.insert(0, java_path)
            # Obtener versión real
            from utils.helpers import get_java_version
            version = get_java_version(java_path)
            if version:
                self.lbl_java_version.configure(text=f"Versión: Java {version}", text_color="#2ecc71")
            else:
                self.lbl_java_version.configure(text="Versión: Detectada (versión desconocida)", text_color="#f1c40f")
        else:
            self.lbl_java_version.configure(text="Versión: No detectada — instala Java 17+", text_color="#e74c3c")

    def _browse_java(self):
        path = filedialog.askopenfilename(title="Seleccionar ejecutable de Java", filetypes=[("Executables", "*.exe"), ("Todos", "*.*")])
        if path:
            self.entry_java.delete(0, 'end')
            self.entry_java.insert(0, path)

    def _save_config(self):
        """Guarda la configuración actual en server.properties."""
        from core.config_manager import ConfigManager
        server_dir = self.get_server_dir()
        cm = ConfigManager(server_dir)
        
        props = {
            'server-port': self.entry_port.get(),
            'motd': self.entry_motd.get(),
            'max-players': self.entry_max_players.get(),
            'difficulty': self.opt_difficulty.get(),
            'gamemode': self.opt_gamemode.get(),
            'online-mode': 'false' if self.switch_offline.get() else 'true',
        }
        cm.write_server_properties(props)
        self.lbl_status_feedback.configure(text="✅ Configuración guardada en server.properties", text_color="#2ecc71")
        if self.on_config_changed:
            self.on_config_changed()

    def _prepare_server(self):
        """Crea la carpeta del servidor, escribe server.properties, acepta EULA."""
        from core.config_manager import ConfigManager
        import os
        
        server_dir = self.get_server_dir()
        cm = ConfigManager(server_dir)
        cm.ensure_server_dir()
        
        # Escribir server.properties con la configuración actual
        props = {
            'server-port': self.entry_port.get(),
            'motd': self.entry_motd.get(),
            'max-players': self.entry_max_players.get(),
            'difficulty': self.opt_difficulty.get(),
            'gamemode': self.opt_gamemode.get(),
            'online-mode': 'false' if self.switch_offline.get() else 'true',
        }
        cm.write_server_properties(props)
        cm.accept_eula()
        
        # Verificar si el JAR o archivos de Forge existen
        jar_path = os.path.join(server_dir, 'server.jar')
        has_forge = False
        if os.path.isdir(server_dir):
            has_forge = any('win_args.txt' in f or 'unix_args.txt' in f for _, _, f in os.walk(server_dir)) or \
                        any(f.startswith('forge-') and f.endswith('.jar') for f in os.listdir(server_dir))
        
        if os.path.isfile(jar_path) or has_forge:
            self.lbl_status_feedback.configure(
                text=f"✅ Servidor preparado y listo para encender ({self.entry_name.get()})",
                text_color="#2ecc71"
            )
        else:
            self.lbl_status_feedback.configure(
                text=f"⚠ Servidor preparado, pero falta descargar el servidor. Haz clic en 'Descargar Servidor'.",
                text_color="#f1c40f"
            )
        if self.on_config_changed:
            self.on_config_changed()

    def get_server_dir(self) -> str:
        """Retorna la ruta absoluta del directorio del servidor actual."""
        from utils.helpers import get_servers_base_dir, sanitize_server_name
        name = sanitize_server_name(self.entry_name.get() or "mi-servidor")
        return os.path.join(get_servers_base_dir(), name)

    def get_server_config(self) -> dict:
        ram_min_val = round(self.slider_ram_min.get() / 512) * 512
        ram_max_val = round(self.slider_ram_max.get() / 512) * 512
        return {
            "name": self.entry_name.get(),
            "engine": self.opt_engine.get(),
            "version": self.opt_version.get(),
            "ram_min": int(ram_min_val),
            "ram_max": int(ram_max_val),
            "port": self.entry_port.get(),
            "java_path": self.entry_java.get(),
        }
