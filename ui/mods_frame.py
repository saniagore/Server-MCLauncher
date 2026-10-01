import customtkinter as ctk
from tkinter import filedialog
import os

class ModsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.mod_manager = None
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # TOP
        self.title_label = ctk.CTkLabel(self, text="🧩 Gestión de Mods", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # INFO
        self.info_label = ctk.CTkLabel(self, text="Nota: Los mods solo son compatibles con servidores Forge o Fabric.", text_color="#3498db")
        self.info_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))
        
        # CENTER
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.empty_label = ctk.CTkLabel(self.scroll_frame, text="No hay mods instalados", text_color="gray50")
        self.empty_label.grid(row=0, column=0, pady=20)
        
        # BOTTOM
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_add = ctk.CTkButton(self.bottom_frame, text="Agregar Mods", fg_color="#2ecc71", hover_color="#27ae60", command=self._add_mods)
        self.btn_add.pack(side="left", padx=5)
        
        self.btn_open = ctk.CTkButton(self.bottom_frame, text="Abrir Carpeta de Mods", command=self._open_mods_folder)
        self.btn_open.pack(side="left", padx=5)
        
        self.btn_refresh = ctk.CTkButton(self.bottom_frame, text="Actualizar Lista", command=self.refresh_mods_list)
        self.btn_refresh.pack(side="left", padx=5)

    def set_mod_manager(self, mod_manager):
        self.mod_manager = mod_manager
        self.refresh_mods_list()

    def refresh_mods_list(self):
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        mods = []
        if self.mod_manager:
            mods = self.mod_manager.list_mods()
            
        if not mods:
            self.empty_label = ctk.CTkLabel(self.scroll_frame, text="No hay mods instalados", text_color="gray50")
            self.empty_label.grid(row=0, column=0, pady=20)
            return
            
        for i, mod in enumerate(mods):
            row = ctk.CTkFrame(self.scroll_frame)
            row.grid(row=i, column=0, sticky="ew", pady=2, padx=5)
            row.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(row, text="📦").grid(row=0, column=0, padx=5)
            
            name = mod['name'] if isinstance(mod, dict) else os.path.basename(str(mod))
            size_text = f" ({mod['size_mb']} MB)" if isinstance(mod, dict) and 'size_mb' in mod else ""
            ctk.CTkLabel(row, text=f"{name}{size_text}").grid(row=0, column=1, sticky="w", padx=5)
            
            btn_remove = ctk.CTkButton(row, text="Eliminar", width=60, fg_color="#e74c3c", hover_color="#c0392b", command=lambda m=name: self._remove_mod(m))
            btn_remove.grid(row=0, column=2, padx=5, pady=5)

    def _add_mods(self):
        files = filedialog.askopenfilenames(title="Seleccionar Mods", filetypes=[("Archivos JAR", "*.jar")])
        if files and self.mod_manager:
            self.mod_manager.add_mods_from_list(list(files))
            self.refresh_mods_list()

    def _remove_mod(self, mod_name: str):
        if self.mod_manager:
            self.mod_manager.remove_mod(mod_name)
            self.refresh_mods_list()

    def _open_mods_folder(self):
        if self.mod_manager:
            self.mod_manager.open_mods_folder()
