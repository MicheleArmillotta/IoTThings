import tkinter as tk
from tkinter import ttk
from gui.tabs.things_tab import create_things_tab
from gui.tabs.services_tab import create_services_tab
from gui.tabs.relationship_tab import create_relationships_tab
from gui.tabs.apps_tab_mod import create_apps_tab
import tkinter as tk
import customtkinter as ctk
def make_scrollable_text(parent):
    text_frame = ctk.CTkFrame(parent, bg="#f9f9f9")
    text_widget = ctk.CTkTextbox(text_frame, wrap="word", bg="white", fg="black", font=("Consolas", 10), relief=tk.FLAT)
    scrollbar = ctk.CTkScrollbar(text_frame, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    return text_frame, text_widget


def launch_gui(context):
    root = ctk.CTk()
    root.title("IoT Space Context")
    #root.attributes("-fullscreen", True)  # Attiva la modalità schermo intero
    # Visualizza l'indirizzo di rete
    ip_label = ctk.CTkLabel(root, text=f"🌐 IDE IP: {context.local_ip}", font=("Arial", 12))
    ip_label.pack(pady=5)    
    def toggle_fullscreen(event=None):
        is_full = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not is_full)

    def end_fullscreen(event=None):
        root.attributes("-fullscreen", False)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", end_fullscreen)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill='both')

    notebook.add(create_things_tab(notebook, context), text="Things")
    notebook.add(create_services_tab(notebook, context), text="Services")
    notebook.add(create_relationships_tab(notebook, context), text="Relationships")
    notebook.add(create_apps_tab(notebook,context), text="Apps")

    #notebook.add(create_apps_tab(notebook, context), text="Apps")

    root.mainloop()
