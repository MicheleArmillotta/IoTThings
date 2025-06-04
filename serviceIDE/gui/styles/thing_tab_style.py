# gui/styles/modern_text_styles.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

def apply_custom_tkinter_settings():
    """Applica le impostazioni di tema globali di CustomTkinter."""
    ctk.set_appearance_mode("dark")  # "dark" o "light"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

def make_scrollable_text(parent):
    """Crea un widget di testo scrollabile con styling moderno CustomTkinter."""
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

def configure_things_text_tags(text_widget):
    """Configura i tag di styling per il testo della Things Tab."""
    # Stile per stato vuoto
    text_widget.tag_config("empty_state",
                           font=("Segoe UI", 16, "bold"),
                           foreground="#6c757d",
                           justify="center")
    text_widget.tag_config("empty_desc",
                           font=("Segoe UI", 12),
                           foreground="#6c757d",
                           justify="center")

    # Stile per il sommario
    text_widget.tag_config("summary",
                           font=("Segoe UI", 12, "bold"),
                           foreground="#0d6efd",
                           spacing1=5, spacing3=10)

    # Stili per le things
    text_widget.tag_config("thing_title",
                           font=("Segoe UI", 16, "bold"),
                           foreground="#198754")
    text_widget.tag_config("thing_count",
                           font=("Segoe UI", 12),
                           foreground="#6c757d")

    # Stili per i campi
    text_widget.tag_config("field_label",
                           font=("Segoe UI", 11, "bold"),
                           foreground="#495057")
    text_widget.tag_config("field_value",
                           font=("JetBrains Mono", 11),
                           foreground="#212529")

    # Stili per le sezioni
    text_widget.tag_config("section_header",
                           font=("Segoe UI", 12, "bold"),
                           foreground="#0d6efd",
                           spacing1=8)

    # Stili per le entità
    text_widget.tag_config("bullet",
                           font=("Segoe UI", 11),
                           foreground="#6610f2")
    text_widget.tag_config("entity_name",
                           font=("Segoe UI", 12, "bold"),
                           foreground="#6f42c1")
    text_widget.tag_config("service_count",
                           font=("Segoe UI", 10),
                           foreground="#6c757d")

    # Stili per i servizi
    text_widget.tag_config("service_item",
                           font=("JetBrains Mono", 10),
                           foreground="#20c997")
    text_widget.tag_config("no_services",
                           font=("Segoe UI", 10, "italic"),
                           foreground="#dc3545")

    # Stili per elementi di separazione
    text_widget.tag_config("separator",
                           foreground="#dee2e6",
                           spacing1=10, spacing3=10)
    text_widget.tag_config("warning",
                           font=("Segoe UI", 11),
                           foreground="#fd7e14")
    text_widget.tag_config("spacing", spacing3=5)