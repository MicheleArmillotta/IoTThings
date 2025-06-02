# gui/tabs/apps_tab.py
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

# Import the GraphicalAppEditor
from gui.app_editor.graphical_app_editor import GraphicalAppEditor
from models.model import IoTApp # Assuming IoTApp is here
from service_discover.api_caller import invoke_iot_app


def create_apps_tab(master, context):
    frame = tk.Frame(master, bg="#f0f0f0")

    apps = []
    selected_app = [None]  # Wrapper to allow assignment in nested function
    apps_listbox = tk.Listbox(frame, bg="white", fg="black", font=("Arial", 10), relief=tk.FLAT)
    list_scroll = ttk.Scrollbar(frame, command=apps_listbox.yview)
    apps_listbox.config(yscrollcommand=list_scroll.set)
    apps_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
    list_scroll.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    detail_text = tk.Text(frame, bg="white", fg="black", font=("Consolas", 10), relief=tk.FLAT)
    detail_scroll = ttk.Scrollbar(frame, command=detail_text.yview)
    detail_text.config(yscrollcommand=detail_scroll.set)
    detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=10)
    detail_scroll.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    def on_finalize_app(app):
        # Check if app already exists (by name) and update, otherwise add new
        for i, existing_app in enumerate(apps):
            if existing_app.name == app.name:
                apps[i] = app
                break
        else:
            apps.append(app)
        apps_listbox.selection_clear(0, tk.END) # Clear selection
        update_apps_list()
        # If the finalized app was the one being edited, re-display its details
        if selected_app[0] and selected_app[0].name == app.name:
            display_app_details(app)


    def update_apps_list():
        apps_listbox.delete(0, tk.END)
        for app in apps:
            apps_listbox.insert(tk.END, app.name)

    def display_app_details(app_to_display):
        detail_text.delete(1.0, tk.END)
        detail_text.insert(tk.END, "📄 Human-Readable Representation:\n\n")
        detail_text.insert(tk.END, app_to_display.__repr__())
        edit_button.pack(side=tk.LEFT, padx=10) # Show the edit button
        run_button.pack(side=tk.LEFT, padx=10)

    def show_app_details_from_listbox(event):
        selection = apps_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        app = apps[index]
        selected_app[0] = app  # Save reference to selected app
        display_app_details(app)

    def upload_app():
        messagebox.showinfo("Upload", "This would open a file dialog to load an app.")
        # For now, just open the editor as if creating a new one or loading conceptually
        GraphicalAppEditor(master, context, on_finalize_app)

    def start_new_app():
        GraphicalAppEditor(master, context, on_finalize_app, existing_app=None)

    def edit_selected_app():
        if selected_app[0]:
            GraphicalAppEditor(master, context, on_finalize_app, existing_app=selected_app[0])

    def run_selected_app():
        if selected_app[0]:
            #from api_caller import invoke_iot_app  # Import here to avoid circular imports
            invoke_iot_app(selected_app[0])

    apps_listbox.bind("<<ListboxSelect>>", show_app_details_from_listbox)

    buttons_frame = tk.Frame(frame, bg="#f0f0f0")
    buttons_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    ttk.Button(buttons_frame, text="📂 Upload Existing App", command=upload_app).pack(side=tk.LEFT, padx=10)
    ttk.Button(buttons_frame, text="✨ Start New App", command=start_new_app).pack(side=tk.LEFT, padx=10)

    # Bottone "Edit App" inizialmente nascosto
    edit_button = ttk.Button(buttons_frame, text="✏️ Edit App", command=edit_selected_app)
    run_button = ttk.Button(buttons_frame, text="▶️ Run App", command=run_selected_app)

    return frame