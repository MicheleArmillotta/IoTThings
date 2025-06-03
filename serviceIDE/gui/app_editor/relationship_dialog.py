import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from models.model import Relationship # Assuming Relationship is in models/model.py

class RelationshipDialog(ctk.CTkToplevel):
    def __init__(self, master, src_node, dst_node, relationship_creation_counter_ref, on_confirm):
        super().__init__(master)
        self.title("Definisci Relazione")
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
        """Configura l'interfaccia utente del dialogo"""
        ctk.CTkLabel(self, text=f"Da: {self.src_node.service.name}").pack(pady=5)
        ctk.CTkLabel(self, text=f"A: {self.dst_node.service.name}").pack(pady=5)

        ctk.CTkLabel(self, text="Tipo Relazione:").pack(pady=5)
        type_menu = ctk.CTkOptionMenu(
            self,
            variable=self.rel_type_var,
            values=["ordered", "on-success", "condition"]
        )
        type_menu.pack(pady=5)

        # Frame condizione (nascosto inizialmente)
        self.cond_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.cond_frame, text="Condizione:").pack(side="left", padx=5)
        self.cond_entry = ctk.CTkEntry(self.cond_frame, textvariable=self.condition_var, width=200)
        self.cond_entry.pack(side="right", padx=5)

        self.rel_type_var.trace("w", self._on_type_change)

        ctk.CTkButton(self, text="Conferma", command=self._confirm_relationship).pack(pady=20)

        # Initial state
        self._on_type_change()

    def _on_type_change(self, *args):
        if self.rel_type_var.get() == "condition":
            self.cond_frame.pack(pady=10)
        else:
            self.cond_frame.pack_forget()

    def _get_relationship_category(self, rel_type):
        """Restituisce la categoria della relazione basata sul tipo"""
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
            messagebox.showerror("Errore", "Inserisci una condizione valida.", parent=self)
            return

        if (rel_type == "condition" and condition and
            not any(condition.startswith(op) for op in ["<", ">", "=", "<=", ">=", "!="])):
            messagebox.showerror("Errore",
                               "La condizione deve iniziare con uno tra <, >, =, <=, >=, !=", parent=self)
            return

        # Increment the counter and get its value
        self.relationship_creation_counter_ref[0] += 1
        current_counter_value = self.relationship_creation_counter_ref[0]

        # Crea l'oggetto Relationship del modello
        relationship_obj = Relationship(
            name=f"{self.src_node.service.name}_to_{self.dst_node.service.name}_{rel_type}_{current_counter_value}",
            category=self._get_relationship_category(rel_type),
            type=rel_type,
            description=condition if condition else rel_type,
            src=self.src_node.service.name,
            dst=self.dst_node.service.name,
            condition=condition
        )

        # Chiama il callback per creare la RelationshipGraph nell'editor
        self.on_confirm(rel_type, condition, relationship_obj, current_counter_value)

        self.destroy()