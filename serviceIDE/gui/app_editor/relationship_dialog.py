import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from models.base_classes import Relationship # Assuming Relationship is in models/model.py
from models.relationship_instance import RelationshipInstance
from models.service_instance import ServiceInstance  # Assuming ServiceInstance is in models/service_instance.py

class RelationshipDialog(ctk.CTkToplevel):
    def __init__(self, master, src_node, dst_node, relationship_creation_counter_ref, on_confirm):
        super().__init__(master)
        self.title("Define Relationship")
        self.geometry("450x350")
        self.grab_set()

        self.src_node = src_node
        self.dst_node = dst_node
        self.relationship_creation_counter_ref = relationship_creation_counter_ref # Pass by reference (list/dict)
        self.on_confirm = on_confirm

        # Variables
        self.rel_type_var = tk.StringVar(value="ordered")
        self.condition_var = tk.StringVar()

        self._setup_ui()

    def _setup_ui(self):
        """Configures the user interface of the dialog"""
        ctk.CTkLabel(self, text=f"From: {self.src_node.get_service_name()}").pack(pady=5)
        ctk.CTkLabel(self, text=f"To: {self.dst_node.get_service_name()}").pack(pady=5)

        ctk.CTkLabel(self, text="Relationship Type:").pack(pady=5)
        type_menu = ctk.CTkOptionMenu(
            self,
            variable=self.rel_type_var,
            values=["ordered", "on-success", "condition"]
        )
        type_menu.pack(pady=5)

        # Condition frame (initially hidden)
        self.cond_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.cond_frame, text="Condition: (first operator then number, e.g. '> 10')").pack(side="left", padx=5)
        self.cond_entry = ctk.CTkEntry(self.cond_frame, textvariable=self.condition_var, width=200)
        self.cond_entry.pack(side="right", padx=5)

        self.rel_type_var.trace("w", self._on_type_change)

        ctk.CTkButton(self, text="Confirm", command=self._confirm_relationship).pack(pady=20)

        # Initial state
        self._on_type_change()

    def _on_type_change(self, *args):
        if self.rel_type_var.get() == "condition":
            self.cond_frame.pack(pady=10)
        else:
            self.cond_frame.pack_forget()

    def _get_relationship_category(self, rel_type):
        """Returns the category of the relationship based on its type"""
        category_map = {
            "ordered": "order",
            "on-success": "order-based",
            "condition": "conditional"
        }
        return category_map.get(rel_type, "order")

    def _confirm_relationship(self):
        rel_type = self.rel_type_var.get()
        condition = self.condition_var.get().strip() if rel_type == "condition" else None

        if rel_type == "condition" and not condition:
            messagebox.showerror("Error", "Enter a valid condition.", parent=self)
            return

        if (rel_type == "condition" and condition and
            not any(condition.startswith(op) for op in ["<", ">", "==", "<=", ">=", "!="])):
            messagebox.showerror("Error",
                               "The condition must start with one of <, >, ==, <=, >=, !=", parent=self)
            return

        # Increment the counter and get its value
        self.relationship_creation_counter_ref[0] += 1
        current_counter_value = self.relationship_creation_counter_ref[0]

        # Create the Relationship object from the model
        relationship_obj = RelationshipInstance.create(
            src_instance=self.src_node.service,
            dst_instance=self.dst_node.service,
            rel_type=rel_type,
            condition=condition
        )

        # Call the callback to create the RelationshipGraph in the editor
        self.on_confirm(rel_type, condition, relationship_obj, current_counter_value)

        self.destroy()