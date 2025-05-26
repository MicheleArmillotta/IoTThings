import tkinter as tk
from tkinter import ttk
from gui.tabs.things_tab import create_things_tab
from gui.tabs.services_tab import create_services_tab
from gui.tabs.relationship_tab import create_relationships_tab
from gui.tabs.apps_tab import create_apps_tab



def launch_gui(context):
    root = tk.Tk()
    root.title("IoT Space Context")
    root.geometry("800x600")

    # Visualizza l'indirizzo di rete
    ip_label = tk.Label(root, text=f"IDE IP: {context.local_ip}", font=("Arial", 12))
    ip_label.pack(pady=5)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill='both')

    notebook.add(create_things_tab(notebook, context), text="Things")
    notebook.add(create_services_tab(notebook, context), text="Services")
    notebook.add(create_relationships_tab(notebook, context), text="Relationships")
    notebook.add(create_apps_tab(notebook,context), text="Apps")

    #notebook.add(create_apps_tab(notebook, context), text="Apps")

    root.mainloop()
