import customtkinter as ctk
from tkinter import simpledialog, messagebox, ttk
import tkinter as tk

# Import custom components and models
from gui.app_editor.canvas_section import AppCanvas # Importa la nuova classe AppCanvas
from gui.app_editor.node_graph import NodeGraph
from gui.app_editor.relationship_graph import RelationshipGraph
from gui.app_editor.relationship_dialog import RelationshipDialog
from models.model import IoTApp, Relationship # Assuming IoTApp and Relationship are here


class GraphicalAppEditor(ctk.CTkToplevel):
    def __init__(self, master, context, on_finalize, existing_app=None):
        super().__init__(master)
        self.title("🧠 Smart IoT App Editor")
        self.context = context
        self.on_finalize = on_finalize
        self.existing_app = existing_app

        # Use a list to allow passing a mutable reference for the counter
        self.relationship_creation_counter = [0] # Counter per ordinamento creazione

        self.geometry("900x600")
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Costanti per la disposizione dei nodi
        self.NODE_WIDTH = 100
        self.NODE_HEIGHT = 60
        self.NODE_SPACING = 100
        self.BASE_X = 300
        self.BASE_Y = 100

        self._setup_ui()
        if self.existing_app:
            self.load_existing_app(self.existing_app)

    def _setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame lista servizi
        listbox_frame = tk.Frame(self)
        listbox_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.service_listbox = tk.Listbox(listbox_frame, width=25, height=20,
                                        yscrollcommand=scrollbar.set)
        self.service_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.config(command=self.service_listbox.yview)

        # Popola la lista servizi
        for svc in self.context.get_services():
            self.service_listbox.insert(tk.END, svc.name)

        self.service_listbox.bind("<Double-Button-1>", self.add_service_node)

        # Canvas principale - ORA È UN'ISTANZA DI AppCanvas
        self.app_canvas = AppCanvas(self)
        self.app_canvas.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Legenda
        self._draw_legend()

        # Frame pulsanti
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Pulsanti
        ctk.CTkButton(button_frame, text="➕ Aggiungi Relazione",
                     command=self.add_relationship).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="🗑️ Elimina Servizio",
                     command=self.delete_selected_nodes).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="👁️ Anteprima Ordine",
                     command=self.show_relationship_order_preview).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="✅ Finalize",
                     command=self.finalize_app).pack(side="right", padx=5)

    def _draw_legend(self):
        """Disegna la legenda delle relazioni (rimane qui come elemento UI)"""
        legend_frame = ctk.CTkFrame(self, width=180)
        legend_frame.grid(row=1, column=2, sticky="ns", padx=5, pady=10)

        ctk.CTkLabel(legend_frame, text="Legenda Relazioni",
                    font=("Arial", 14, "bold")).pack(pady=(5, 10))

        items = [
            ("Relazione Ordinata", "black"),
            ("On Success", "green"),
            ("Condizionale", "purple"),
        ]

        for label, color in items:
            item_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2, padx=5)
            canvas = tk.Canvas(item_frame, width=20, height=10, highlightthickness=0)
            canvas.create_line(0, 5, 20, 5, fill=color, width=3)
            canvas.pack(side="left")
            ctk.CTkLabel(item_frame, text=label).pack(side="left", padx=5)

    def load_existing_app(self, app):
        """Carica un'app esistente sul canvas"""
        self.app_canvas.clear_canvas() # Assicurati di pulire prima

        svc_to_node = {}

        for i, svc in enumerate(app.services):
            x = self.BASE_X
            y = self.BASE_Y + i * self.NODE_SPACING
            node = self.app_canvas.add_node(svc, x, y)
            svc_to_node[svc.name] = node

        for rel in app.relationships:
            src_node = svc_to_node.get(rel.src)
            dst_node = svc_to_node.get(rel.dst)
            if src_node and dst_node:
                # Re-crea la RelationshipGraph con l'oggetto Relationship del modello
                self.app_canvas.add_relationship(
                    src_node, dst_node,
                    rel.type,
                    rel.condition,
                    relationship_obj=rel, # Passa l'oggetto Relationship
                    creation_order_value=self.relationship_creation_counter[0] # Imposta un ordine di creazione
                )
                self.relationship_creation_counter[0] += 1

    def add_service_node(self, event=None):
        """Aggiunge un nuovo nodo servizio al canvas"""
        line_index = self.service_listbox.curselection()
        if not line_index:
            return

        svc = self.context.get_services()[line_index[0]]

        # Calcola posizione automatica
        x = self.BASE_X
        y = self.BASE_Y + self.NODE_SPACING * len(self.app_canvas.get_nodes())

        self.app_canvas.add_node(svc, x, y)

    def delete_selected_nodes(self):
        """Elimina i nodi selezionati e le loro relazioni"""
        selected_nodes = self.app_canvas.selected_nodes # Ottieni la lista dei nodi selezionati dal canvas
        if not selected_nodes:
            messagebox.showwarning("Selezione vuota", "Seleziona almeno un nodo da eliminare.")
            return

        nodes_to_delete_ids = [node.id for node in selected_nodes]

        for node_id in nodes_to_delete_ids:
            self.app_canvas.delete_node(node_id) # Delega la cancellazione al canvas

        self.app_canvas.deselect_all_nodes() # Delega la deselezione al canvas


    def add_relationship(self):
        """Aggiunge una relazione tra nodi selezionati"""
        selected_nodes = self.app_canvas.selected_nodes # Ottieni la lista dei nodi selezionati dal canvas
        if len(selected_nodes) != 2:
            messagebox.showwarning("Selezione invalida",
                                 "Seleziona esattamente 2 nodi per creare una relazione.")
            return

        src_node = selected_nodes[0]
        dst_node = selected_nodes[1]

        # Verifica che non esista già una relazione identica
        if self._relationship_exists(src_node, dst_node):
            messagebox.showwarning("Relazione esistente",
                                 "Esiste già una relazione tra questi nodi.")
            return

        # Open the relationship dialog
        RelationshipDialog(
            self, src_node, dst_node,
            self.relationship_creation_counter, # Pass the mutable list
            self._on_relationship_dialog_confirm
        )

    def _on_relationship_dialog_confirm(self, rel_type, condition, relationship_obj, creation_order_value):
        """Callback dalla RelationshipDialog quando una relazione è confermata."""
        selected_nodes = self.app_canvas.selected_nodes
        src_node = selected_nodes[0] # These are still the selected nodes when dialog opens
        dst_node = selected_nodes[1]

        self.app_canvas.add_relationship(src_node, dst_node, rel_type, condition, relationship_obj, creation_order_value)

        # Deseleziona nodi nel canvas
        self.app_canvas.deselect_all_nodes()


    def _relationship_exists(self, src_node, dst_node):
        """Verifica se esiste già una relazione tra due nodi"""
        # Ora accedi alle relazioni tramite app_canvas
        return any(
            rel.src_node_id == src_node.id and rel.dst_node_id == dst_node.id
            for rel in self.app_canvas.get_relationships()
        )

    def sort_relationships_by_position(self):
        """Ordina le relazioni basandosi sulla posizione Y dei nodi di destinazione"""
        # Accedi ai nodi e relazioni tramite app_canvas
        relationships = self.app_canvas.get_relationships()
        nodes = self.app_canvas.get_nodes()

        def get_dst_node_y(rel_graph):
            dst_node = self.app_canvas.find_node_by_id(rel_graph.dst_node_id)
            return dst_node.y if dst_node else float('inf')

        relationships.sort(key=get_dst_node_y)
        self.app_canvas.redraw_relationships() # Delega il ridisegno al canvas

        messagebox.showinfo("Ordinamento Completato",
                           f"Le {len(relationships)} relazioni sono state ordinate "
                           "in base alla posizione dei nodi di destinazione nel canvas.")

    def show_relationship_order_preview(self):
        """Mostra l'anteprima dell'ordine delle relazioni"""
        relationships = self.app_canvas.get_relationships()
        if not relationships:
            messagebox.showwarning("Nessuna Relazione", "Non ci sono relazioni da ordinare.")
            return

        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Anteprima Ordine Relazioni")
        preview_window.geometry("600x500")
        preview_window.grab_set()

        content_frame = ctk.CTkFrame(preview_window)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(content_frame, text="Ordine Attuale delle Relazioni",
                    font=("Arial", 16, "bold")).pack(pady=(10, 20))

        text_widget = tk.Text(content_frame, height=20, width=70,
                             font=("Consolas", 10), wrap=tk.WORD)
        scrollbar_preview = ttk.Scrollbar(content_frame, orient="vertical",
                                        command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar_preview.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar_preview.pack(side="right", fill="y")

        def populate_preview():
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, "ORDINE ATTUALE:\n" + "="*60 + "\n\n")

            for i, rel_graph in enumerate(relationships, 1):
                src_node = self.app_canvas.find_node_by_id(rel_graph.src_node_id)
                dst_node = self.app_canvas.find_node_by_id(rel_graph.dst_node_id)

                src_y = src_node.y if src_node else 0
                dst_y = dst_node.y if dst_node else 0

                text_widget.insert(tk.END, f"{i}. {rel_graph.get_display_name()}\n")
                text_widget.insert(tk.END, f"   ID: {rel_graph.id[:8]}...\n")
                text_widget.insert(tk.END, f"   Tipo: {rel_graph.type.upper()}\n")
                if rel_graph.condition:
                    text_widget.insert(tk.END, f"   Condizione: {rel_graph.condition}\n")
                text_widget.insert(tk.END, f"   Posizione src: Y={src_y}, dst: Y={dst_y}\n")
                text_widget.insert(tk.END, f"   Ordine creazione: {rel_graph.creation_order}\n")
                text_widget.insert(tk.END, "\n")

        populate_preview()

        button_frame = ctk.CTkFrame(preview_window)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        def apply_sorting():
            self.sort_relationships_by_position()
            populate_preview()

        ctk.CTkButton(button_frame, text="🔄 Ordina per Posizione",
                     command=apply_sorting).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="✅ Chiudi",
                     command=preview_window.destroy).pack(side="right", padx=5, pady=10)

    def finalize_app(self):
        nodes = self.app_canvas.get_nodes()
        relationships = self.app_canvas.get_relationships()

        if not nodes:
            messagebox.showwarning("App vuota", "Aggiungi almeno un servizio prima di finalizzare.")
            return

        if relationships:
            result = messagebox.askyesnocancel(
                "Ordinamento Relazioni",
                "Vuoi ordinare le relazioni in base alla posizione dei nodi prima di finalizzare?"
            )

            if result is None:
                return
            elif result:
                    self.sort_relationships_by_position()

        services = [node.service for node in nodes]
        relationship_objects = [rel.relationship_obj for rel in relationships]



        if self.existing_app:
            app = IoTApp.from_data(self.existing_app.name, services, relationship_objects)
        else:
            name = simpledialog.askstring("Nome App", "Inserisci nome per l'app:")
            if not name:
                return
            app = IoTApp.from_data(name, services, relationship_objects)

        self.on_finalize(app)
        self.destroy()