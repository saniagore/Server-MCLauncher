#!/usr/bin/env python3
"""MCServerManager - Gestor de Servidores Minecraft No Premium"""

import sys
import os

# Asegurar que el directorio del script esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.main_window import MainWindow


def main():
    """Punto de entrada principal de la aplicación."""
    # Configuración global de CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    
    # Crear y ejecutar la ventana principal
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
