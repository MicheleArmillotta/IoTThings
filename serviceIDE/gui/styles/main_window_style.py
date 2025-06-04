# gui/styles/gui_styles.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

def apply_custom_tkinter_settings():
    """Applica le impostazioni di tema globali di CustomTkinter."""
    ctk.set_appearance_mode("dark")  # "dark" o "light"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

def make_scrollable_text(parent):
    """Crea un widget di testo scrollabile con styling moderno CustomTkinter.
       Questa versione è generica e usa CustomTkinter per i frame e le scrollbar.
    """
    # Frame principale con bordi arrotondati
    text_frame = ctk.CTkFrame(
        parent,
        corner_radius=12,
        fg_color=("gray95", "gray20"),
        border_width=1,
        border_color=("gray80", "gray40")
    )

    # Text widget con styling personalizzato
    text_widget = tk.Text(
        text_frame,
        wrap="word",
        bg=("#ffffff", "#2b2b2b")[ctk.get_appearance_mode().lower() == "dark"],
        fg=("#000000", "#ffffff")[ctk.get_appearance_mode().lower() == "dark"],
        font=("JetBrains Mono", 11),
        relief=tk.FLAT,
        borderwidth=0,
        padx=15,
        pady=15,
        selectbackground=("#0078d4", "#264f78")[ctk.get_appearance_mode().lower() == "dark"],
        insertbackground=("#000000", "#ffffff")[ctk.get_appearance_mode().lower() == "dark"],
        spacing1=2,
        spacing3=2
    )

    # Scrollbar personalizzata
    scrollbar = ctk.CTkScrollbar(
        text_frame,
        command=text_widget.yview,
        width=16,
        corner_radius=8
    )
    text_widget.config(yscrollcommand=scrollbar.set)

    # Posizionamento con padding
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 5), pady=15)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=15)

    return text_frame, text_widget