import os
import customtkinter as ctk
from core.server_process import ServerProcess
from core.config_manager import ConfigManager
from core.mod_manager import ModManager
from core.connectivity import ConnectivityManager
from ui.console_frame import ConsoleFrame
from ui.config_frame import ConfigFrame
from ui.mods_frame import ModsFrame
from ui.connectivity_frame import ConnectivityFrame
from utils.helpers import get_servers_base_dir, sanitize_server_name

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MCServerManager")
        self.geometry("1100x750")
        self.minsize(900, 600)

        self.server_process = None
        self.connectivity_manager = ConnectivityManager()

        self._build_ui()
        # Conectar el ConnectivityManager al frame
        self.connectivity_frame.set_connectivity_manager(self.connectivity_manager)
        # Inicializar ModManager para el servidor configurado
        self._update_mods_manager()
        self.tabview.configure(command=self._on_tab_change)
        
        # Conectar actualización en tiempo real del sidebar
        self.config_frame.on_config_changed = self._refresh_sidebar_info
        self.after(500, self._refresh_sidebar_info)
        
        # Manejo de cierre seguro de la ventana
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _on_window_close(self):
        if self.connectivity_manager:
            try:
                self.connectivity_manager.stop_tunnel()
            except Exception:
                pass
                
        if self.server_process and self.server_process.is_running:
            from tkinter import messagebox
            confirm = messagebox.askyesno(
                "Servidor en Ejecución",
                "El servidor de Minecraft está corriendo.\n¿Deseas guardar el mundo y apagarlo de forma segura antes de salir?"
            )
            if confirm:
                self.server_process.stop()
                import time
                for _ in range(30):
                    if not self.server_process.is_running:
                        break
                    time.sleep(0.1)
            else:
                return
        self.destroy()

    def _on_tab_change(self):
        self._refresh_sidebar_info()
        if self.tabview.get() == "🧩 Mods":
            self._update_mods_manager()

    def _update_mods_manager(self):
        server_dir = self._resolve_server_dir()
        self.mods_frame.set_mod_manager(ModManager(server_dir))

    def _refresh_sidebar_info(self):
        try:
            config = self.config_frame.get_server_config()
            self.info_version.configure(text=f"Versión: {config.get('version', '---')}")
            self.info_engine.configure(text=f"Motor: {config.get('engine', '---')}")
            ram_min = f"{int(config.get('ram_min', 1024))}M"
            ram_max = f"{int(config.get('ram_max', 4096))}M"
            self.info_ram.configure(text=f"RAM: {ram_min} / {ram_max}")
            self.info_port.configure(text=f"Puerto: {config.get('port', '25565')}")
        except Exception:
            pass

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # LEFT SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="⛏ MCServerManager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Indicador de estado
        self.status_label = ctk.CTkLabel(self.sidebar, text="🔴 Detenido", text_color="#e74c3c", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        # Botones de control
        self.start_button = ctk.CTkButton(self.sidebar, text="Encender Servidor", fg_color="#2ecc71", hover_color="#27ae60", command=self._start_server)
        self.start_button.grid(row=2, column=0, padx=20, pady=10)

        self.stop_button = ctk.CTkButton(self.sidebar, text="Apagar Servidor", fg_color="#e74c3c", hover_color="#c0392b", state="disabled", command=self._stop_server)
        self.stop_button.grid(row=3, column=0, padx=20, pady=10)

        self.separator1 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        self.separator1.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        # Info del servidor
        self.info_version = ctk.CTkLabel(self.sidebar, text="Versión: ---")
        self.info_version.grid(row=5, column=0, padx=20, pady=5, sticky="w")

        self.info_engine = ctk.CTkLabel(self.sidebar, text="Motor: ---")
        self.info_engine.grid(row=6, column=0, padx=20, pady=5, sticky="w")

        self.info_ram = ctk.CTkLabel(self.sidebar, text="RAM: ---")
        self.info_ram.grid(row=7, column=0, padx=20, pady=5, sticky="w")

        self.info_port = ctk.CTkLabel(self.sidebar, text="Puerto: ---")
        self.info_port.grid(row=8, column=0, padx=20, pady=5, sticky="nw")

        self.separator2 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray30")
        self.separator2.grid(row=9, column=0, sticky="ew", padx=20, pady=10)

        self.version_label = ctk.CTkLabel(self.sidebar, text="v1.0.0", text_color="gray50")
        self.version_label.grid(row=10, column=0, padx=20, pady=10)

        # RIGHT CONTENT AREA
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tabview.add("🖥 Consola")
        self.tabview.add("⚙ Configuración")
        self.tabview.add("🧩 Mods")
        self.tabview.add("🌐 Conectividad")

        # Inicializar frames
        self.console_frame = ConsoleFrame(self.tabview.tab("🖥 Consola"))
        self.console_frame.pack(expand=True, fill="both")
        self.console_frame.set_command_callback(self._send_command_to_server)

        self.config_frame = ConfigFrame(self.tabview.tab("⚙ Configuración"))
        self.config_frame.pack(expand=True, fill="both")

        self.mods_frame = ModsFrame(self.tabview.tab("🧩 Mods"))
        self.mods_frame.pack(expand=True, fill="both")

        self.connectivity_frame = ConnectivityFrame(self.tabview.tab("🌐 Conectividad"))
        self.connectivity_frame.pack(expand=True, fill="both")

    def _resolve_server_dir(self) -> str:
        """Resuelve el directorio del servidor basado en la configuración actual."""
        config = self.config_frame.get_server_config()
        name = sanitize_server_name(config.get("name", "mi-servidor"))
        return os.path.join(get_servers_base_dir(), name)

    def _start_server(self):
        config = self.config_frame.get_server_config()
        server_dir = self._resolve_server_dir()

        # Verificar que server.jar o archivos de Forge existan
        has_jar = os.path.isfile(os.path.join(server_dir, "server.jar"))
        has_forge = False
        if os.path.isdir(server_dir):
            has_forge = any('win_args.txt' in f or 'unix_args.txt' in f for _, _, f in os.walk(server_dir)) or \
                        any(f.startswith('forge-') and f.endswith('.jar') for f in os.listdir(server_dir))
        
        if not has_jar and not has_forge:
            self.console_frame.append_line("[MCServerManager] ❌ No se encontró server.jar ni archivos de Forge. Ve a Configuración → Descargar/Preparar Servidor primero.")
            self.tabview.set("⚙ Configuración")
            return

        # Convertir RAM de MB a formato Java (ej: 1024 → '1024M')
        ram_min = f"{int(config.get('ram_min', 1024))}M"
        ram_max = f"{int(config.get('ram_max', 4096))}M"
        java_path = config.get("java_path", "java") or "java"

        # Limpiar session.lock residual de sesiones previas para evitar bloqueos
        lock_file = os.path.join(server_dir, "world", "session.lock")
        if os.path.isfile(lock_file):
            try:
                os.remove(lock_file)
            except Exception:
                pass

        self.server_process = ServerProcess(
            server_dir=server_dir,
            jar_name="server.jar",
            ram_min=ram_min,
            ram_max=ram_max,
            java_path=java_path,
        )

        success = self.server_process.start(
            on_output=self._on_server_output,
            on_stopped=self._on_server_stopped,
        )

        if success:
            self._update_status(True)
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.tabview.set("🖥 Consola")
            # Actualizar sidebar info
            self.info_version.configure(text=f"Versión: {config.get('version', '---')}")
            self.info_engine.configure(text=f"Motor: {config.get('engine', '---')}")
            self.info_ram.configure(text=f"RAM: {ram_min} / {ram_max}")
            self.info_port.configure(text=f"Puerto: {config.get('port', '25565')}")
            # Configurar ModManager para la pestaña de mods
            mod_manager = ModManager(server_dir)
            self.mods_frame.set_mod_manager(mod_manager)
        else:
            self.console_frame.append_line("[MCServerManager] ❌ Error al iniciar el servidor. Revisa la ruta de Java.")
            self.server_process = None

    def _stop_server(self):
        if self.server_process:
            self.server_process.stop()
            self.console_frame.append_line("[MCServerManager] Enviando comando stop... Espera a que el servidor guarde el mundo.")

    def _send_command_to_server(self, command: str):
        if self.server_process and self.server_process.is_running:
            self.server_process.send_command(command)
            self.console_frame.append_line(f"> {command}")
        else:
            self.console_frame.append_line("[MCServerManager] El servidor no está en ejecución.")

    def _on_server_output(self, line: str):
        self.after(0, self.console_frame.append_line, line)

    def _on_server_stopped(self):
        self.after(0, self._handle_server_stopped)

    def _handle_server_stopped(self):
        self._update_status(False)
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.console_frame.append_line("[MCServerManager] ✅ Servidor detenido.")
        self.server_process = None

    def _update_status(self, running: bool):
        if running:
            self.status_label.configure(text="🟢 Ejecutando", text_color="#2ecc71")
        else:
            self.status_label.configure(text="🔴 Detenido", text_color="#e74c3c")
