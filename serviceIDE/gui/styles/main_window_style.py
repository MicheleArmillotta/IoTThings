import customtkinter as ctk

def apply_main_window_style(root):
    # Imposta modalità e tema globale
    ctk.set_appearance_mode("dark")  # "dark" o "light"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
    # Imposta colore di sfondo della finestra principale
    root.configure(fg_color="#23272e")