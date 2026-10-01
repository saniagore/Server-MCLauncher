import customtkinter as ctk
import threading
import tkinter as tk

class ConnectivityFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.manager = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # --- Section: Información de Red ---
        self.frame_network = ctk.CTkFrame(self)
        self.frame_network.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.frame_network.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.frame_network, text="Información de Red", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        self.lbl_ip_local = ctk.CTkLabel(self.frame_network, text="IP Local: Detectando...")
        self.lbl_ip_local.grid(row=1, column=0, sticky="w", padx=10, pady=2)
        
        self.lbl_port = ctk.CTkLabel(self.frame_network, text="Puerto: 25565")
        self.lbl_port.grid(row=2, column=0, sticky="w", padx=10, pady=2)
        
        self.lbl_lan = ctk.CTkLabel(self.frame_network, text="Dirección LAN: ---:25565")
        self.lbl_lan.grid(row=3, column=0, sticky="w", padx=10, pady=2)
        
        self.btn_copy_lan = ctk.CTkButton(self.frame_network, text="Copiar IP LAN", width=120, command=self._copy_lan_ip)
        self.btn_copy_lan.grid(row=3, column=1, sticky="w", padx=10, pady=2)

        # --- Section: Túnel ---
        self.frame_tunnel = ctk.CTkFrame(self)
        self.frame_tunnel.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.frame_tunnel.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frame_tunnel, text="Túnel para Juego Online", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(self.frame_tunnel, text="Un túnel permite que tus amigos se conecten sin tener que abrir puertos en tu router.", text_color="gray70", wraplength=400, justify="left").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.seg_tunnel = ctk.CTkSegmentedButton(self.frame_tunnel, values=["playit.gg", "ngrok"])
        self.seg_tunnel.set("playit.gg")
        self.seg_tunnel.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        
        self.tunnel_status = ctk.CTkLabel(self.frame_tunnel, text="🔴 Túnel Detenido", text_color="#e74c3c", font=ctk.CTkFont(weight="bold"))
        self.tunnel_status.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        controls = ctk.CTkFrame(self.frame_tunnel, fg_color="transparent")
        controls.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        
        self.btn_start_tunnel = ctk.CTkButton(controls, text="Iniciar Túnel", fg_color="#2ecc71", hover_color="#27ae60", command=self._start_tunnel)
        self.btn_start_tunnel.pack(side="left", padx=(0, 10))
        
        self.btn_stop_tunnel = ctk.CTkButton(controls, text="Detener Túnel", fg_color="#e74c3c", hover_color="#c0392b", state="disabled", command=self._stop_tunnel)
        self.btn_stop_tunnel.pack(side="left")
        
        self.tunnel_console = ctk.CTkTextbox(self.frame_tunnel, height=100, font=("Consolas", 12), fg_color="#1a1a2e", text_color="#00ff41")
        self.tunnel_console.grid(row=5, column=0, sticky="ew", padx=10, pady=10)
        self.tunnel_console.configure(state="disabled")

        # --- Section: Instrucciones ---
        self.frame_guide = ctk.CTkFrame(self)
        self.frame_guide.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.frame_guide, text="Instrucciones para tus amigos", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        guide_text = "1. Si juegan en la misma red Wi-Fi/LAN, dales la 'Dirección LAN' de arriba.\n"
        guide_text += "2. Si juegan desde otras casas, inicia un túnel (ej. playit.gg) y espera a que aparezca la IP generada en los logs.\n"
        guide_text += "3. Dales la IP generada por el túnel. Deberán agregarla en Minecraft -> Multijugador -> Añadir Servidor."
        
        ctk.CTkLabel(self.frame_guide, text=guide_text, justify="left", wraplength=450).pack(anchor="w", padx=10, pady=5)

        self.refresh_network_info()

    def set_connectivity_manager(self, manager):
        self.manager = manager

    def refresh_network_info(self):
        def detect():
            if self.manager:
                ip = self.manager.get_local_ip()
            else:
                import socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    ip = s.getsockname()[0]
                    s.close()
                except Exception:
                    ip = "127.0.0.1"
            self.after(0, lambda: self._set_network_labels(ip))
        
        import threading
        threading.Thread(target=detect, daemon=True).start()
    
    def _set_network_labels(self, ip: str):
        self.lbl_ip_local.configure(text=f"IP Local: {ip}")
        self.lbl_lan.configure(text=f"Dirección LAN: {ip}:25565")

    def _copy_lan_ip(self):
        ip = self.lbl_lan.cget("text").split(": ", 1)[-1]
        self.clipboard_clear()
        self.clipboard_append(ip)

    def _start_tunnel(self):
        if not self.manager:
            return
        
        tunnel_type = self.seg_tunnel.get()
        self._update_tunnel_status(True)
        self.btn_start_tunnel.configure(state="disabled")
        self.btn_stop_tunnel.configure(state="normal")
        
        self.tunnel_console.configure(state="normal")
        self.tunnel_console.insert("end", f"Iniciando túnel {tunnel_type}...\n")
        self.tunnel_console.configure(state="disabled")
        
        def run():
            if tunnel_type == "playit.gg":
                if not self.manager.check_playit_installed():
                    self.after(0, lambda: self._append_tunnel_line("❌ playit.gg no está instalado. Descárgalo desde https://playit.gg"))
                    self.after(0, lambda: self._update_tunnel_status(False))
                    self.after(0, lambda: self.btn_start_tunnel.configure(state="normal"))
                    self.after(0, lambda: self.btn_stop_tunnel.configure(state="disabled"))
                    return
                self.manager.start_playit_tunnel(on_output=self._on_tunnel_output)
            else:
                if not self.manager.check_ngrok_installed():
                    self.after(0, lambda: self._append_tunnel_line("❌ ngrok no está instalado. Descárgalo desde https://ngrok.com"))
                    self.after(0, lambda: self._update_tunnel_status(False))
                    self.after(0, lambda: self.btn_start_tunnel.configure(state="normal"))
                    self.after(0, lambda: self.btn_stop_tunnel.configure(state="disabled"))
                    return
                self.manager.start_ngrok_tunnel(on_output=self._on_tunnel_output)
        
        import threading
        threading.Thread(target=run, daemon=True).start()

    def _stop_tunnel(self):
        if self.manager:
            self.manager.stop_tunnel()
        self._update_tunnel_status(False)
        self.btn_start_tunnel.configure(state="normal")
        self.btn_stop_tunnel.configure(state="disabled")
        
        self.tunnel_console.configure(state="normal")
        self.tunnel_console.insert("end", "Túnel detenido.\n")
        self.tunnel_console.configure(state="disabled")

    def _update_tunnel_status(self, running: bool):
        if running:
            self.tunnel_status.configure(text="🟢 Túnel Ejecutándose", text_color="#2ecc71")
        else:
            self.tunnel_status.configure(text="🔴 Túnel Detenido", text_color="#e74c3c")

    def _on_tunnel_output(self, line: str):
        self.after(0, self._append_tunnel_line, line)
        
    def _append_tunnel_line(self, line: str):
        self.tunnel_console.configure(state="normal")
        self.tunnel_console.insert("end", line + "\n")
        self.tunnel_console.see("end")
        self.tunnel_console.configure(state="disabled")
