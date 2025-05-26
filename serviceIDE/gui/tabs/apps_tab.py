import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk

# Mock App representation
class IoTApp: #utilizzarla come "contesto delle app"
    def __init__(self, name, services=None, relationships=None):
        self.name = name
        self.services = services if services else []
        self.relationships = relationships if relationships else []

# Editor for composing IoT Apps
class AppEditor(tk.Toplevel):
    def __init__(self, master, context, on_finalize):
        super().__init__(master)
        self.title("IoT App Editor")
        self.context = context
        self.on_finalize = on_finalize
        self.selected_services = []
        self.composition = []  # Tuples of (service_name, relationship_type)

        self.ordered_relationships = []
        self.order_based_relationships = []
        self.condition_based_relationships = []

        # Layout setup
        self.grid_columnconfigure(1, weight=1)

        # Section 1: Available Services
        available_label = tk.Label(self, text="Available Services")
        available_label.grid(row=0, column=0, padx=10, pady=5)

        self.available_listbox = tk.Listbox(self)
        for service in context.get_services():
            self.available_listbox.insert(tk.END, f"{service.name} ({service.thing_name})")
        self.available_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="ns")

        # Drag & Drop button
        self.add_btn = tk.Button(self, text="Add →", command=self.add_service_to_composition)
        self.add_btn.grid(row=1, column=1, pady=5)

        # Section 2: Composition Area
        composition_label = tk.Label(self, text="Compose App")
        composition_label.grid(row=0, column=2, padx=10, pady=5)

        self.composition_frame = tk.Frame(self)
        self.composition_frame.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")
        self.composition_frame.grid_columnconfigure(1, weight=1)

        self.composition_widgets = []

        # Action Buttons
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.clear_button = tk.Button(btn_frame, text="Clear", command=self.clear_editor)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.finalize_button = tk.Button(btn_frame, text="Finalize", command=self.finalize_app)
        self.finalize_button.pack(side=tk.RIGHT, padx=5)

    def add_service_to_composition(self):
        selected = self.available_listbox.curselection()
        for index in selected:
            service_entry = self.available_listbox.get(index)
            service_name = service_entry.split(" (")[0]

            row = len(self.composition_widgets)
            lbl = tk.Label(self.composition_frame, text=service_name)
            lbl.grid(row=row, column=0, sticky="w")

            self.composition_widgets.append(service_name)

            # Handle relationships
            if row >= 1:
                prev_service = self.composition_widgets[-2]
                current_service = self.composition_widgets[-1]

                rel_type = simpledialog.askstring(
                    "Relationship Type",
                    f"Define relationship from {prev_service} to {current_service}:\nType 1 = ordered,\nType 2 = order-based if completed,\nType 3 = conditional",
                    parent=self
                )

                if rel_type == "1":
                    self.ordered_relationships.append((prev_service, current_service))
                elif rel_type == "2":
                    self.order_based_relationships.append((prev_service, current_service))
                elif rel_type == "3":
                    condition = simpledialog.askstring(
                        "Condition",
                        f"Define condition for {prev_service} → {current_service}: e.g. > 10",
                        parent=self
                    )
                    if condition:
                        self.condition_based_relationships.append((prev_service, current_service, condition))
                else:
                    messagebox.showwarning("Invalid Input", "Unknown relationship type. Defaulting to ordered.")
                    self.ordered_relationships.append((prev_service, current_service))

                # Optional: warn if no relationship exists in context ->>>>>>>>>>>>>>>>>>>> TODO
                if not self.check_relationship_exists(prev_service, current_service):
                    messagebox.showwarning("Missing Relationship", f"No defined relationship between {prev_service} and {current_service}")

    def check_relationship_exists(self, src, dst):
        for rel in self.context.get_relationships():
            if rel.src == src and rel.dst == dst:
                return True
        return False

    def clear_editor(self):
        for widget in self.composition_frame.winfo_children():
            widget.destroy()
        self.composition_widgets.clear()
        self.ordered_relationships.clear()
        self.order_based_relationships.clear()
        self.condition_based_relationships.clear()

    def finalize_app(self):
        if not self.composition_widgets:
            messagebox.showwarning("Empty App", "Add services to your app before finalizing.")
            return

        name = simpledialog.askstring("Finalize App", "Enter a name for your IoT App:")
        if not name:
            return

        services = self.composition_widgets.copy()
        # For now, just combine all relationship types for mockup
        relationships = self.ordered_relationships + self.order_based_relationships + self.condition_based_relationships
        new_app = IoTApp(name, services, relationships) # -> questo NO, creare un altra classe che gestisce questo
        self.on_finalize(new_app)
        self.destroy()


def create_apps_tab(master, context):
    frame = tk.Frame(master)
    apps_listbox = tk.Listbox(frame)
    apps_listbox.pack(fill=tk.BOTH, expand=True)

    apps = []  # List of finalized apps

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

    buttons_frame = tk.Frame(frame)
    buttons_frame.pack(pady=10)

    upload_btn = tk.Button(buttons_frame, text="Upload Existing App", command=upload_app)
    upload_btn.pack(side=tk.LEFT, padx=5)

    new_btn = tk.Button(buttons_frame, text="Start New App", command=start_new_app)
    new_btn.pack(side=tk.LEFT, padx=5)

    return frame
