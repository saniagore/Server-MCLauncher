import customtkinter as ctk
from typing import Callable

class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.command_callback = None
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # TOP
        self.title_label = ctk.CTkLabel(self, text="📋 Consola del Servidor", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # CENTER
        self.textbox = ctk.CTkTextbox(
            self, 
            font=("Consolas", 13), 
            fg_color="#1a1a2e", 
            text_color="#00ff41",
            state="disabled"
        )
        self.textbox.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        
        # Configure tags for colors
        self.textbox.tag_config("error", foreground="#e74c3c")
        self.textbox.tag_config("warn", foreground="#f1c40f")
        self.textbox.tag_config("info", foreground="#2ecc71")
        self.textbox.tag_config("join", foreground="#00bcd4")
        
        # BOTTOM ROW
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        
        self.entry = ctk.CTkEntry(self.bottom_frame, placeholder_text="Escribe un comando...")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self._send_command())
        
        self.send_btn = ctk.CTkButton(self.bottom_frame, text="Enviar", width=80, command=self._send_command)
        self.send_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_btn = ctk.CTkButton(self.bottom_frame, text="Limpiar", width=80, fg_color="#7f8c8d", hover_color="#95a5a6", command=self.clear)
        self.clear_btn.grid(row=0, column=2)
        
        self.line_count = 0

    def set_command_callback(self, callback: Callable[[str], None]):
        self.command_callback = callback

    def _send_command(self):
        cmd = self.entry.get()
        if cmd and self.command_callback:
            self.command_callback(cmd)
            self.entry.delete(0, 'end')

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        self.line_count = 0

    def append_line(self, line: str):
        tag = self._colorize_line(line)
        self.textbox.configure(state="normal")
        
        # Limit to 5000 lines
        if self.line_count >= 5000:
            self.textbox.delete("1.0", "2.0")
        else:
            self.line_count += 1
            
        if not line.endswith("\n"):
            line += "\n"
            
        self.textbox.insert("end", line, tag)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def _colorize_line(self, line: str) -> str:
        line_lower = line.lower()
        if "error" in line_lower or "exception" in line_lower:
            return "error"
        if "warn" in line_lower:
            return "warn"
        if "info" in line_lower:
            return "info"
        if "joined the game" in line_lower or "left the game" in line_lower:
            return "join"
        return "info"
