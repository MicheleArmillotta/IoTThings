import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from models.model import IoTApp, Relationship, Service

class AppEditor(tk.Toplevel):
    def __init__(self, master, context, on_finalize):
        super().__init__(master)
        self.title("🛠️ IoT App Editor")
        self.context = context
        self.on_finalize = on_finalize
        self.selected_services = []
        self.relationships = []

        self.configure(bg="#f0f0f0")
        self.grid_columnconfigure(1, weight=1)

        # Available Services
        ttk.Label(self, text="Available Services", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5)
        self.available_listbox = tk.Listbox(self, bg="white", fg="black", font=("Arial", 10), relief=tk.FLAT)
        for service in context.get_services():
            self.available_listbox.insert(tk.END, f"{service.name} ({service.thing_name})")
        list_scroll = ttk.Scrollbar(self, command=self.available_listbox.yview)
        self.available_listbox.config(yscrollcommand=list_scroll.set)
        self.available_listbox.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="ns")
        list_scroll.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="nse")

        # Add button
        self.add_btn = ttk.Button(self, text="Add →", command=self.add_service_to_composition)
        self.add_btn.grid(row=1, column=1, padx=5, pady=5)

        # Composition Area
        ttk.Label(self, text="Compose App", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, pady=5)
        self.composition_canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.composition_frame = tk.Frame(self.composition_canvas, bg="white")
        self.composition_scroll = ttk.Scrollbar(self, command=self.composition_canvas.yview)
        self.composition_canvas.config(yscrollcommand=self.composition_scroll.set)
        self.composition_canvas.create_window((0, 0), window=self.composition_frame, anchor="nw")
        self.composition_frame.bind("<Configure>", lambda e: self.composition_canvas.configure(scrollregion=self.composition_canvas.bbox("all")))

        self.composition_canvas.grid(row=1, column=2, padx=(10, 0), pady=5, sticky="nsew")
        self.composition_scroll.grid(row=1, column=2, padx=(0, 10), sticky="nse")
        self.composition_widgets = []

        # Action Buttons
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="🧹 Clear", command=self.clear_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Finalize", command=self.finalize_app).pack(side=tk.RIGHT, padx=5)

    def add_service_to_composition(self):
        selected = self.available_listbox.curselection()
        for index in selected:
            service_entry = self.available_listbox.get(index)
            service_name = service_entry.split(" (")[0]
            service_obj = next((s for s in self.context.get_services() if s.name == service_name), None)
            if not service_obj:
                continue

            row = len(self.composition_widgets)
            label = ttk.Label(self.composition_frame, text=service_name, background="white")
            label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            self.composition_widgets.append(service_obj)

            if row >= 1:
                prev_service = self.composition_widgets[-2]
                current_service = self.composition_widgets[-1]

                rel_type = simpledialog.askstring(
                    "Relationship Type",
                    f"Define relationship from {prev_service.name} to {current_service.name}:\n"
                    "Type 1 = ordered\nType 2 = order-based if completed\nType 3 = conditional",
                    parent=self
                )

                if rel_type == "1":
                    category, rtype, desc = "order", "ordered", "Simple order"
                elif rel_type == "2":
                    category, rtype, desc = "order-based", "on-success", "Executes on successful completion"
                elif rel_type == "3":
                    condition = simpledialog.askstring("Condition", f"Define condition (e.g. > 10):", parent=self)
                    if not condition:
                        messagebox.showwarning("Missing Condition", "No condition defined. Skipping.")
                        return
                    category, rtype, desc = "conditional", "condition", "Conditional execution"
                    rel = Relationship(
                        name=f"{prev_service.name}_to_{current_service.name}",
                        category=category,
                        type=rtype,
                        description=desc,
                        src=prev_service,
                        dst=current_service,
                        condition=condition
                    )
                else:
                    messagebox.showwarning("Invalid Input", "Unknown relationship type. Defaulting to ordered.")
                    category, rtype, desc = "order", "ordered", "Default ordered"

                if rel_type in ["1", "2"]:
                    rel = Relationship(
                        name=f"{prev_service.name}_to_{current_service.name}",
                        category=category,
                        type=rtype,
                        description=desc,
                        src=prev_service,
                        dst=current_service
                    )

                self.relationships.append(rel)

    def clear_editor(self):
        for widget in self.composition_frame.winfo_children():
            widget.destroy()
        self.composition_widgets.clear()
        self.relationships.clear()

    def finalize_app(self):
        if not self.composition_widgets:
            messagebox.showwarning("Empty App", "Add services to your app before finalizing.")
            return

        name = simpledialog.askstring("Finalize App", "Enter a name for your IoT App:")
        if not name:
            return

        new_app = IoTApp.from_data(name, self.composition_widgets, self.relationships)
        self.on_finalize(new_app)
        self.destroy()


def create_apps_tab(master, context):
    frame = tk.Frame(master, bg="#f0f0f0")

    apps = []
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
        apps.append(app)
        update_apps_list()

    def update_apps_list():
        apps_listbox.delete(0, tk.END)
        for app in apps:
            apps_listbox.insert(tk.END, app.name)

    def upload_app():
        messagebox.showinfo("Upload", "This would open a file dialog to load an app.")
        AppEditor(master, context, on_finalize_app)

    def start_new_app():
        AppEditor(master, context, on_finalize_app)

    def show_app_details(event):
        selection = apps_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        app = apps[index]
        detail_text.delete(1.0, tk.END)
        detail_text.insert(tk.END, "📄 Human-Readable Representation:\n\n")
        detail_text.insert(tk.END, app.__repr__())

    apps_listbox.bind("<<ListboxSelect>>", show_app_details)

    buttons_frame = tk.Frame(frame, bg="#f0f0f0")
    buttons_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    ttk.Button(buttons_frame, text="📂 Upload Existing App", command=upload_app).pack(side=tk.LEFT, padx=10)
    ttk.Button(buttons_frame, text="✨ Start New App", command=start_new_app).pack(side=tk.LEFT, padx=10)

    return frame