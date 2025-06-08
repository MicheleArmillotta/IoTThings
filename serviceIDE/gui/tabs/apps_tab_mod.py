# gui/tabs/apps_tab.py
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
import os
import json
from models.base_classes import Service, Relationship

from gui.app_editor.graphical_app_editor import GraphicalAppEditor
from models.iot_app import IoTApp
from service_discover.api_caller import invoke_iot_app
import threading

def read_workdir_from_file():
    config_path = os.path.join(os.path.dirname(__file__), "workdir_path")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            path = f.read().strip()
            if os.path.isdir(path):
                return path
    return os.getcwd()

def create_apps_tab(master, context):
    frame = tk.Frame(master, bg="#f0f0f0")
    initial_dir = read_workdir_from_file()
    workdir = [initial_dir] 
    apps = []
    selected_app = [None]
    display_app = [None]
    apps_listbox = tk.Listbox(frame, bg="white", fg="black", font=("Arial", 16), relief=tk.FLAT)
    list_scroll = ttk.Scrollbar(frame, command=apps_listbox.yview)
    apps_listbox.config(yscrollcommand=list_scroll.set)
    apps_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
    list_scroll.pack(side=tk.LEFT, fill=tk.Y, pady=10)

    # Vertical frame for details and prompt
    right_frame = tk.Frame(frame, bg="#f0f0f0")
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=10)

    # App details (upper part)
    detail_text = tk.Text(right_frame, bg="white", fg="black", font=("Consolas", 15), relief=tk.FLAT, height=15)
    detail_scroll = ttk.Scrollbar(right_frame, command=detail_text.yview)
    detail_text.config(yscrollcommand=detail_scroll.set)
    detail_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # Prompt (lower part)
    prompt_frame = tk.Frame(right_frame, bg="#f0f0f0")
    prompt_text = tk.Text(prompt_frame, height=20, width=60, font=("Consolas", 14), bg="black", fg="lime", insertbackground="white")
    prompt_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    prompt_text.config(state="disabled")
    prompt_frame.pack_forget()  # Hide the prompt at startup

    def on_finalize_app(app):
        for i, existing_app in enumerate(apps):
            if existing_app.id == app.id:
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
        display_app.append(app_to_display.name)
        display_app.append(app_to_display.name)
        edit_button.pack(side=tk.TOP, fill=tk.X, pady=5)
        run_stop_button.pack(side=tk.TOP, fill=tk.X, pady=5)
        save_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    def elimnate_display():
        detail_text.delete(1.0, tk.END)
        detail_text.insert(tk.END, "")
        display_app[0] = None
        edit_button.pack_forget()
        run_stop_button.pack_forget()
        save_button.pack_forget()

    def show_app_details_from_listbox(event):
        selection = apps_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        app = apps[index]
        selected_app[0] = app
        display_app_details(app)

    def start_new_app():
        GraphicalAppEditor(master, context, on_finalize_app, existing_app=None)

    def edit_selected_app():
        if selected_app[0]:
            GraphicalAppEditor(master, context, on_finalize_app, existing_app=selected_app[0])
            update_apps_list()
            detail_text.delete(1.0, tk.END)
            selected_app[0] = None

    app_thread = [None]  # To keep track of the thread
    stop_flag = [{"stop": False}]  # List for mutability

    is_running = [False]  # Mutable state

    def run_or_stop_app():
        if not is_running[0]:
            # Start the app
            if selected_app[0]:
                prompt_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(40, 0))
                prompt_text.config(state="normal")
                prompt_text.delete("1.0", tk.END)
                prompt_text.config(state="disabled")
                stop_flag[0]["stop"] = False

                def app_runner():
                    invoke_iot_app(
                        selected_app[0],
                        write_fn=lambda text: write_to_prompt(prompt_text, text),
                        input_fn=lambda msg: get_user_input(prompt_text, msg),
                        stop_flag=stop_flag[0]
                    )
                    prompt_text.configure(state="disabled")
                    is_running[0] = False
                    run_stop_button.configure(text="▶️ Run App", fg_color="#1ab126", hover_color="#179922", text_color="#ffffff")
                app_thread[0] = threading.Thread(target=app_runner, daemon=True)
                app_thread[0].start()
                is_running[0] = True
                run_stop_button.configure(text="⏹️ Stop App", fg_color="#ff0c03", hover_color="#b30000", text_color="#ffffff")
        else:
            # Stop the app
            stop_flag[0]["stop"] = True
            is_running[0] = False
            run_stop_button.configure(text="▶️ Run App", fg_color="#1ab126", hover_color="#179922", text_color="#ffffff")

    apps_listbox.bind("<<ListboxSelect>>", show_app_details_from_listbox)

    buttons_frame = tk.Frame(frame, bg="#f0f0f0")
    buttons_frame.pack(side=tk.LEFT, padx=(10, 0), pady=10, fill=tk.Y)

    # --- Buttons, now vertical ---
    ctk.CTkButton(buttons_frame, text="📂 Explore saved App", fg_color="#e63119", hover_color="#aa120c", text_color="#ffffff", command=lambda: upload_app(workdir[0], on_finalize_app, apps, update_apps_list, elimnate_display, frame)).pack(side=tk.TOP, fill=tk.X, pady=5)
    set_workdir_button = ctk.CTkButton(buttons_frame, text="📁 Set Workdir", fg_color="#e69e19", hover_color="#996311", command=lambda: choose_workdir(workdir))
    ctk.CTkButton(buttons_frame, text="✨ Start New App", command=start_new_app).pack(side=tk.TOP, fill=tk.X, pady=5)
    edit_button = ctk.CTkButton(buttons_frame, text="✏️ Edit App", fg_color="#5c1ea3", hover_color="#3e0b79", text_color="#ffffff", command=edit_selected_app)
    run_stop_button = ctk.CTkButton(buttons_frame, text="▶️ Run App", fg_color="#1ab126", hover_color="#179922", text_color="#ffffff", command=run_or_stop_app)    
    save_button = ctk.CTkButton(buttons_frame, text="💾 Save App", command=lambda: save_selected_app(selected_app[0], workdir[0]))

    # Hidden by default
    edit_button.pack_forget()
    run_stop_button.pack_forget()
    save_button.pack_forget()
    set_workdir_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    return frame

def write_to_prompt(prompt_widget, text):
    """Helper function to write text to prompt widget and scroll to end"""
    prompt_widget.config(state="normal")
    prompt_widget.insert(tk.END, text)
    prompt_widget.see(tk.END)
    prompt_widget.update()
    prompt_widget.config(state="normal")
    
def get_user_input(prompt_widget, message):
    # Enable the prompt for input
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
    # Return to read-only after input
    prompt_widget.config(state="disabled")

    return user_input[0] if user_input[0] is not None else ""

def choose_workdir(workdir_ref):
    """Opens the file dialog to choose the working directory"""
    new_dir = filedialog.askdirectory(title="Select Working Directory")
    if new_dir:
        workdir_ref[0] = new_dir
        print(f"[INFO] Working directory set to: {new_dir}")

        # Save the new path in the config file
        config_path = os.path.join(os.path.dirname(__file__), "workdir_path")
        with open(config_path, "w") as f:
            f.write(new_dir)

def save_selected_app(app, workdir_path):
    if not app:
        messagebox.showwarning("No App Selected", "Please select an app to save.")
        return

    try:
        filename = os.path.join(workdir_path, f"{app.name}.iot")

        if os.path.exists(filename):
            confirm = messagebox.askyesno("File Exists",
                                          f"A file named '{app.name}.iot' already exists.\nDo you want to overwrite it?")
            if not confirm:
                messagebox.showinfo("Cancelled", "Save cancelled by user.")
                return

        app_data = app.to_dict()

        with open(filename, "w") as f:
            json.dump(app_data, f, indent=4)

        messagebox.showinfo("Success", f"App saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save app: {e}")

def upload_app(workdir_path, on_finalize_app, current_apps: list, update_app_list, eliminate_display, frame):
    def load_and_finalize(filename):
        full_path = os.path.join(workdir_path, filename)
        try:
            with open(full_path, "r") as f:
                app_dict = json.load(f)
            app = IoTApp.from_dict(app_dict)
            # Block if it already exists
            print("App id to upload:", app.id)
            print("Current app ids:", [a.id for a in current_apps])
            if any(existing_app.id == app.id for existing_app in current_apps):     
                messagebox.showwarning("App Already Uploaded", f"The app '{app.name}' is already uploaded.")
                return
            on_finalize_app(app)
            messagebox.showinfo("Upload Successful", f"App '{app.name}' uploaded successfully.")
            popup.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load app: {e}")

    def delete_selected_app():
        selected = combo.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an app file to delete.")
            return

        full_path = os.path.join(workdir_path, selected)
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected}'?")
        if confirm:
            try:
                os.remove(full_path)
                app_name = os.path.splitext(selected)[0]
                # Remove from current list
                for app in current_apps:
                    if app.name == app_name:
                        current_apps.remove(app)
                       
                        eliminate_display()
                        update_app_list()
                        break
                messagebox.showinfo("Deleted", f"App '{selected}' deleted.")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete app: {e}")

    # Find .iot files in the workdir
    app_files = [f for f in os.listdir(workdir_path) if f.endswith(".iot")]

    if not app_files:
        messagebox.showinfo("No Apps Found", "No .iot apps found in the working directory.")
        return

    # Create popup
    popup = ctk.CTkToplevel()
    popup.title("Upload IoT App")
    popup.geometry("400x250")
    popup.transient(frame.winfo_toplevel())  # master is the main window or the main frame
    popup.grab_set()

    label = ctk.CTkLabel(popup, text="Select an App to Upload or Delete", font=("Arial", 16))
    label.pack(pady=10)

    combo = ctk.CTkComboBox(popup, values=app_files, width=300)
    combo.pack(pady=10)

    button_frame = ctk.CTkFrame(popup)
    button_frame.pack(pady=20)

    upload_btn = ctk.CTkButton(button_frame, text="Upload", command=lambda: load_and_finalize(combo.get()))
    upload_btn.pack(side="left", padx=10)

    delete_btn = ctk.CTkButton(button_frame, text="Delete", fg_color="red", command=delete_selected_app)
    delete_btn.pack(side="left", padx=10)
