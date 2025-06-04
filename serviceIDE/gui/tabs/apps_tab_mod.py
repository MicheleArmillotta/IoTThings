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
    selected_app = [None]
    apps_listbox = tk.Listbox(frame, bg="white", fg="black", font=("Arial", 10), relief=tk.FLAT)
    list_scroll = ttk.Scrollbar(frame, command=apps_listbox.yview)
    apps_listbox.config(yscrollcommand=list_scroll.set)
    apps_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
    list_scroll.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    # Frame verticale per dettagli e prompt
    right_frame = tk.Frame(frame, bg="#f0f0f0")
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=10)

    # Dettagli app (parte superiore)
    detail_text = tk.Text(right_frame, bg="white", fg="black", font=("Consolas", 10), relief=tk.FLAT, height=15)
    detail_scroll = ttk.Scrollbar(right_frame, command=detail_text.yview)
    detail_text.config(yscrollcommand=detail_scroll.set)
    detail_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Prompt (parte inferiore)
    prompt_frame = tk.Frame(right_frame, bg="#f0f0f0")
    prompt_text = tk.Text(prompt_frame, height=8, width=60, font=("Consolas", 10), bg="black", fg="lime", insertbackground="white")
    prompt_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    prompt_text.config(state="disabled")
    prompt_frame.pack_forget()  # Nascondi il prompt all'avvio


    def on_finalize_app(app):
        for i, existing_app in enumerate(apps):
            if existing_app.name == app.name:
                apps[i] = app
                break
        else:
            apps.append(app)
        apps_listbox.selection_clear(0, tk.END)
        update_apps_list()
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
        edit_button.pack(side=tk.LEFT, padx=10)
        run_button.pack(side=tk.LEFT, padx=10)

    def show_app_details_from_listbox(event):
        selection = apps_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        app = apps[index]
        selected_app[0] = app
        display_app_details(app)

    def upload_app():
        messagebox.showinfo("Upload", "This would open a file dialog to load an app.")
        GraphicalAppEditor(master, context, on_finalize_app)

    def start_new_app():
        GraphicalAppEditor(master, context, on_finalize_app, existing_app=None)

    def edit_selected_app():
        if selected_app[0]:
            GraphicalAppEditor(master, context, on_finalize_app, existing_app=selected_app[0])

    def run_selected_app():
        if selected_app[0]:
            prompt_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(40, 0))
            prompt_text.config(state="normal")
            prompt_text.delete("1.0", tk.END)
            prompt_text.config(state="disabled")
            # Passa il widget prompt_text (o la funzione write_to_prompt) a invoke_iot_app
            invoke_iot_app(selected_app[0],  
                           write_fn=lambda text: write_to_prompt(prompt_text, text),
                           input_fn=lambda msg: get_user_input(prompt_text, msg))
            prompt_text.config(state="disabled")

    apps_listbox.bind("<<ListboxSelect>>", show_app_details_from_listbox)

    buttons_frame = tk.Frame(frame, bg="#f0f0f0")
    buttons_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    ttk.Button(buttons_frame, text="📂 Upload Existing App", command=upload_app).pack(side=tk.LEFT, padx=10)
    ttk.Button(buttons_frame, text="✨ Start New App", command=start_new_app).pack(side=tk.LEFT, padx=10)

    edit_button = ttk.Button(buttons_frame, text="✏️ Edit App", command=edit_selected_app)
    run_button = ttk.Button(buttons_frame, text="▶️ Run App", command=run_selected_app)

    return frame

def write_to_prompt(prompt_widget, text):
    """Helper function to write text to prompt widget and scroll to end"""
    prompt_widget.config(state="normal")
    prompt_widget.insert(tk.END, text)
    prompt_widget.see(tk.END)
    prompt_widget.update()
    prompt_widget.config(state="normal")
def get_user_input(prompt_widget, message):
    # Abilita il prompt per l'input
    prompt_widget.config(state="disabled")
    write_to_prompt(prompt_widget, f"$ {message}")

    user_input = [None]
    input_complete = [False]

    def on_key_press(event):
        if event.keysym == 'Return':
            content = prompt_widget.get("1.0", tk.END)
            lines = content.strip().split('\n')
            last_line = lines[-1] if lines else ""
            prompt_start = f"$ {message}"
            if last_line.startswith(prompt_start):
                user_input[0] = last_line[len(prompt_start):].strip()
            else:
                user_input[0] = last_line.strip()
            input_complete[0] = True
            write_to_prompt(prompt_widget, "\n")
            return "break"

    prompt_widget.bind("<KeyPress-Return>", on_key_press)
    prompt_widget.focus_set()

    while not input_complete[0]:
        prompt_widget.update()
        prompt_widget.after(50)

    prompt_widget.unbind("<KeyPress-Return>")
    # Torna in sola lettura dopo l'input
    prompt_widget.config(state="disabled")

    return user_input[0] if user_input[0] is not None else ""
