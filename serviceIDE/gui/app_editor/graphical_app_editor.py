import customtkinter as ctk
from tkinter import simpledialog, messagebox, ttk
import tkinter as tk

# Import custom components and models
from gui.app_editor.canvas_section import AppCanvas # Importa la nuova classe AppCanvas
from gui.app_editor.node_graph import NodeGraph
from gui.app_editor.relationship_graph import RelationshipGraph
from gui.app_editor.relationship_dialog import RelationshipDialog
from models.iot_app import IoTApp 
from customtkinter import CTkInputDialog
from tkinter.messagebox import showinfo
from models.service_instance import ServiceInstance


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

       # Frame laterale unico per input e legenda
        self.side_frame = ctk.CTkFrame(self)
        self.side_frame.grid(row=1, column=2, sticky="ns", padx=5, pady=10)

        # Frame input (in alto)
        self.input_frame = ctk.CTkFrame(self.side_frame)
        self.input_frame.pack(side="top", fill="x", pady=(0, 20))
        self.input_frame.grid_propagate(False)

        self.input_title = ctk.CTkLabel(self.input_frame, text="Configura Input", font=("Arial", 14, "bold"))
        self.input_title.pack(pady=(5, 10))

        self.input_widgets = {}
        self.input_save_btn = ctk.CTkButton(self.input_frame, text="Salva Input", command=self.save_node_inputs)
        self.input_save_btn.pack(pady=10)

        # Frame legenda (in basso)
        self.legend_frame = ctk.CTkFrame(self.side_frame)
        self.legend_frame.pack(side="bottom", fill="x", pady=(20, 0))
        self._draw_legend(self.legend_frame)
        
        # Frame pulsanti
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Pulsanti
        ctk.CTkButton(button_frame, text="➕ Aggiungi Relazione",
                     command=self.add_relationship).pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="🗑️ Elimina Servizio",
                     command=self.delete_selected_nodes).pack(side="left", padx=5)

        """ ctk.CTkButton(button_frame, text="👁️ Anteprima Ordine",
                     command=self.show_relationship_order_preview).pack(side="left", padx=5)"""
        ctk.CTkButton(button_frame, text="✅ Finalize",
                     command=self.finalize_app).pack(side="right", padx=5)
        
        save_button = ctk.CTkButton(
        button_frame,  # oppure self se non hai una toolbar
        text="Salva",
        command=self.handle_save
        )
        save_button.pack(side="left", padx=10)

    def _draw_legend(self, legend_frame):
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

        for i, svc in enumerate(app.service_instances):
            x = self.BASE_X
            y = self.BASE_Y + i * self.NODE_SPACING
            node = self.app_canvas.add_node(svc, x, y)
            svc_to_node[svc.id] = node

        for rel in app.relationship_instances:
            src_node = svc_to_node.get(rel.get_src_id())
            dst_node = svc_to_node.get(rel.get_dst_id())
            if src_node and dst_node:
                # Re-crea la RelationshipGraph con l'oggetto Relationship del modello
                self.app_canvas.add_relationship(
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
        service_instance = ServiceInstance.create_from_service(svc)
        # Calcola posizione automatica
        x = self.BASE_X
        y = self.BASE_Y + self.NODE_SPACING * len(self.app_canvas.get_nodes())

        self.app_canvas.add_node(service_instance, x, y)

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

        self.app_canvas.add_relationship(rel_type, condition, relationship_obj, creation_order_value)

        # Deseleziona nodi nel canvas
        self.app_canvas.deselect_all_nodes()


    def _relationship_exists(self, src_node, dst_node):
        """Verifica se esiste già una relazione tra due nodi (stessa direzione)"""
        return any(
            rel.get_src_id() == src_node.service.id and rel.get_dst_id() == dst_node.service.id
            for rel in self.app_canvas.get_relationships()
        )

    def sort_relationships_by_position(self):
        """Ordina le relazioni basandosi sulla posizione Y dei nodi di destinazione"""
        # Accedi ai nodi e relazioni tramite app_canvas
        relationships = self.app_canvas.get_relationships()
        nodes = self.app_canvas.get_nodes()

        def get_dst_node_y(rel_graph):
            dst_node = self.app_canvas.find_node_by_id(rel_graph.get_dst_id())
            return dst_node.y if dst_node else float('inf')

        relationships.sort(key=get_dst_node_y)
        self.app_canvas.relationships = relationships

        self.app_canvas.redraw_relationships() # Delega il ridisegno al canvas

        messagebox.showinfo("Ordinamento Completato",
                           f"Le {len(relationships)} relazioni sono state ordinate "
                           "in base alla posizione dei nodi di destinazione nel canvas.")

    """ def show_relationship_order_preview(self):
        #Mostra l'anteprima dell'ordine delle relazioni
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
    """
    # ...existing imports...
    @staticmethod
    def topological_sort_nodes(nodes, relationships):
        """Restituisce i nodi ordinati topologicamente secondo le relazioni."""
        id_to_node = {node.service.id: node for node in nodes}
        graph = {node.service.id: [] for node in nodes}
        in_degree = {node.service.id: 0 for node in nodes}

        for rel in relationships:
            src_id = rel.get_src_id()
            dst_id = rel.get_dst_id()
            if src_id in graph and dst_id in graph:
                graph[src_id].append(dst_id)
                in_degree[dst_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        ordered = []

        while queue:
            current = queue.pop(0)
            ordered.append(id_to_node[current])
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Se ci sono cicli, aggiungi i rimanenti
        for nid in in_degree:
            if in_degree[nid] > 0 and id_to_node[nid] not in ordered:
                ordered.append(id_to_node[nid])

        return ordered
    
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

        ordered_nodes = self.topological_sort_nodes(nodes, relationships)
        services = [node.service for node in ordered_nodes]
        relationship_objects = [rel.relationship_instance for rel in relationships]
        if self.existing_app:
            app = IoTApp.from_data(self.existing_app.name, services, relationship_objects, exist=True, id=self.existing_app.id)
        else:
            name = simpledialog.askstring("Nome App", "Inserisci nome per l'app:")
            if not name:
                return
            app = IoTApp.from_data(name, services, relationship_objects, exist=False)
        self.on_finalize(app)
        self.destroy()
        
        
    def update_input_panel(self):
        selected_nodes = self.app_canvas.selected_nodes
        # Mostra solo se è selezionato UN nodo e ha input da configurare
        if len(selected_nodes) == 1:
            node = selected_nodes[0]
            service_instance = node.service
            input_params = getattr(service_instance.service, "input_params", {})
            if input_params:
                # Pulisci vecchi widget (label + entry)
                for widget in getattr(self, "input_widgets_all", []):
                    widget.destroy()
                self.input_widgets_all = []
                self.input_widgets = {}
                # Crea un campo per ogni input
                for param, param_type in input_params.items():
                    val = service_instance.input_values.get(param, "")
                    label = ctk.CTkLabel(self.input_frame, text=f"{param} ({param_type}):")
                    label.pack()
                    entry = ctk.CTkEntry(self.input_frame)
                    entry.insert(0, str(val))
                    entry.pack()
                    self.input_widgets[param] = entry
                    self.input_widgets_all.extend([label, entry])
                self.input_frame.pack(side="top", fill="x", pady=(0, 20))  # Mostra il frame
                return
        # Se non ci sono input o selezione multipla, nascondi
        for widget in getattr(self, "input_widgets_all", []):
            widget.destroy()
        self.input_widgets_all = []
        self.input_widgets = {}
        self.input_frame.pack_forget()
            
    def save_node_inputs(self):
        selected_nodes = self.app_canvas.selected_nodes
        if len(selected_nodes) == 1:
            node = selected_nodes[0]
            service_instance = node.service
            updated_values = {}
            for param, entry in self.input_widgets.items():
                value = entry.get()
                service_instance.input_values[param] = value
                updated_values[param] = value

            # Aggiorna anche tutte le ServiceInstance nelle relazioni con lo stesso id
            for rel in self.app_canvas.get_relationships():
                # Controlla src
                if hasattr(rel, "relationship_instance"):
                    src = getattr(rel.relationship_instance, "src", None)
                    if src and src.id == service_instance.id and src is not service_instance:
                        src.input_values.update(updated_values)
                    dst = getattr(rel.relationship_instance, "dst", None)
                    if dst and dst.id == service_instance.id and dst is not service_instance:
                        dst.input_values.update(updated_values)

            messagebox.showinfo("Input salvati", "Gli input sono stati salvati nel servizio selezionato e nelle relazioni collegate.")

    def handle_save(self):
        dialog = ctk.CTkInputDialog(text="Inserisci il nome del progetto:", title="Salva progetto")
        name = dialog.get_input()
        if name:
            self.app_canvas.save_graphical_app_editor(name)
            showinfo("Salvataggio completato", f"Progetto '{name}' salvato con successo.")