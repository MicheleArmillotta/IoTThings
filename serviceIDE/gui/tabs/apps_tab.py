import customtkinter as ctk
from tkinter import simpledialog, messagebox, ttk
import tkinter as tk
import math
import uuid
from models.model import IoTApp, Relationship

class NodeGraph:
    """Rappresenta un nodo nel canvas con tutte le sue proprietà"""
    
    def __init__(self, service, x, y, canvas_id=None, text_id=None):
        self.id = str(uuid.uuid4())  # ID univoco per il nodo
        self.service = service
        self.x = x
        self.y = y
        self.canvas_id = canvas_id  # ID dell'elemento canvas (ovale)
        self.text_id = text_id      # ID del testo nel canvas
        self.is_selected = False
        self.width = 100
        self.height = 60
    
    def get_center(self):
        """Restituisce il centro del nodo"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def get_bottom_center(self):
        """Restituisce il punto centrale del bordo inferiore"""
        return (self.x + self.width // 2, self.y + self.height)
    
    def get_top_center(self):
        """Restituisce il punto centrale del bordo superiore"""
        return (self.x + self.width // 2, self.y)
    
    def contains_point(self, x, y):
        """Verifica se un punto è all'interno del nodo"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def update_position(self, new_x, new_y):
        """Aggiorna la posizione del nodo"""
        self.x = new_x
        self.y = new_y
    
    def __str__(self):
        return f"NodeGraph(id={self.id[:8]}, service={self.service.name}, pos=({self.x},{self.y}))"

class RelationshipGraph:
    """Rappresenta una relazione nel canvas con tutte le sue proprietà"""
    
    def __init__(self, src_node, dst_node, rel_type, condition=None, relationship_obj=None):
        self.id = str(uuid.uuid4())  # ID univoco per la relazione
        self.src_node_id = src_node.id
        self.dst_node_id = dst_node.id
        self.src_service = src_node.service
        self.dst_service = dst_node.service
        self.type = rel_type
        self.condition = condition
        self.relationship_obj = relationship_obj  # Oggetto Relationship del modello
        
        # Elementi canvas
        self.line_id = None         # ID della linea nel canvas
        self.condition_label_id = None  # ID dell'etichetta condizione
        
        # Proprietà visive
        self.color = self._get_color_by_type()
        
        # Timestamp per ordinamento
        self.creation_order = 0
    
    def _get_color_by_type(self):
        """Restituisce il colore basato sul tipo di relazione"""
        color_map = {
            "ordered": "black",
            "on-success": "green", 
            "condition": "purple"
        }
        return color_map.get(self.type, "black")
    
    def get_display_name(self):
        """Restituisce un nome descrittivo per la relazione"""
        base_name = f"{self.src_service.name} → {self.dst_service.name}"
        if self.condition:
            return f"{base_name} ({self.condition})"
        return f"{base_name} ({self.type})"
    
    def __str__(self):
        return f"RelationshipGraph(id={self.id[:8]}, {self.get_display_name()})"

class GraphicalAppEditor(ctk.CTkToplevel):
    def __init__(self, master, context, on_finalize,existing_app=None):
        super().__init__(master)
        self.title("🧠 Smart IoT App Editor")
        self.context = context
        self.on_finalize = on_finalize
        self.existing_app = existing_app

        # Usa le nuove classi per gestire nodi e relazioni
        self.nodes = []  # Lista di NodeGraph
        self.relationships = []  # Lista di RelationshipGraph
        self.relationship_creation_counter = 0  # Counter per ordinamento creazione
        
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

        # Variabili per il drag & drop
        self.dragged_node = None
        self.drag_offset = (0, 0)
        self.selected_nodes = []

        self._setup_ui()
        if self.existing_app:
            self.load_existing_app(self.existing_app)

    def load_existing_app(self, app):
        svc_to_node = {}

        for i, svc in enumerate(app.services):
            x = self.BASE_X
            y = self.BASE_Y + i * self.NODE_SPACING

            canvas_id = self.canvas.create_oval(
                x, y, x + self.NODE_WIDTH, y + self.NODE_HEIGHT,
                fill="#b3d9ff", tags="node"
            )

            text_id = self.canvas.create_text(
                x + self.NODE_WIDTH // 2, y + self.NODE_HEIGHT // 2,
                text=svc.name, tags="node"
            )

            node = NodeGraph(svc, x, y, canvas_id, text_id)
            self.nodes.append(node)
            svc_to_node[svc.name] = node

        for rel in app.relationships:
            src_node = svc_to_node.get(rel.src.name)
            dst_node = svc_to_node.get(rel.dst.name)
            if src_node and dst_node:
                rel_graph = RelationshipGraph(
                    src_node, dst_node,
                    rel.type,
                    rel.condition,
                    relationship_obj=rel
                )
                rel_graph.creation_order = self.relationship_creation_counter
                self.relationship_creation_counter += 1
                self.relationships.append(rel_graph)
                self._draw_relationship(rel_graph)


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

        # Canvas principale
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.select_node)
        self.canvas.bind("<B1-Motion>", self.drag_node)
        self.canvas.bind("<ButtonRelease-1>", self.release_node)

        # Legenda
        self.draw_legend()

        # Frame pulsanti
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Pulsanti
        ctk.CTkButton(button_frame, text="✅ Finalize", 
                     command=self.finalize_app).pack(side="right", padx=5)
        
        ctk.CTkButton(button_frame, text="➕ Aggiungi Relazione", 
                     command=self.add_relationship).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🗑️ Elimina Servizio", 
                     command=self.delete_selected_nodes).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="👁️ Anteprima Ordine", 
                     command=self.show_relationship_order_preview).pack(side="left", padx=5)

    def draw_legend(self):
        """Disegna la legenda delle relazioni"""
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

    def add_service_node(self, event=None):
        """Aggiunge un nuovo nodo servizio al canvas"""
        line_index = self.service_listbox.curselection()
        if not line_index:
            return
            
        svc = self.context.get_services()[line_index[0]]
        
        # Calcola posizione automatica
        x = self.BASE_X
        y = self.BASE_Y + self.NODE_SPACING * len(self.nodes)

        # Crea gli elementi canvas
        canvas_id = self.canvas.create_oval(
            x, y, x + self.NODE_WIDTH, y + self.NODE_HEIGHT,
            fill="#b3d9ff", tags="node"
        )
        
        text_id = self.canvas.create_text(
            x + self.NODE_WIDTH//2, y + self.NODE_HEIGHT//2,
            text=svc.name, tags="node"
        )

        # Crea il NodeGraph
        node = NodeGraph(svc, x, y, canvas_id, text_id)
        self.nodes.append(node)

    def find_node_by_canvas_id(self, canvas_id):
        """Trova un nodo basandosi sull'ID dell'elemento canvas"""
        for node in self.nodes:
            if canvas_id in (node.canvas_id, node.text_id):
                return node
        return None

    def find_node_by_id(self, node_id):
        """Trova un nodo basandosi sul suo ID univoco"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def select_node(self, event):
        """Gestisce la selezione dei nodi"""
        clicked_items = self.canvas.find_closest(event.x, event.y)
        node = self.find_node_by_canvas_id(clicked_items[0])
        
        if node:
            if node in self.selected_nodes:
                # Deseleziona
                self.selected_nodes.remove(node)
                node.is_selected = False
                self.canvas.itemconfig(node.canvas_id, outline="black", width=1)
            else:
                # Seleziona
                self.selected_nodes.append(node)
                node.is_selected = True
                self.canvas.itemconfig(node.canvas_id, outline="red", width=3)

    def drag_node(self, event):
        """Gestisce il trascinamento dei nodi"""
        if not self.dragged_node:
            clicked_items = self.canvas.find_withtag("current")
            if clicked_items:
                node = self.find_node_by_canvas_id(clicked_items[0])
                if node:
                    self.dragged_node = node
                    self.drag_offset = (event.x - node.x, event.y - node.y)
            return

        # Aggiorna posizione
        node = self.dragged_node
        dx, dy = self.drag_offset
        new_x = event.x - dx
        new_y = event.y - dy
        
        node.update_position(new_x, new_y)
        
        # Aggiorna canvas
        self.canvas.coords(node.canvas_id, new_x, new_y, 
                          new_x + node.width, new_y + node.height)
        self.canvas.coords(node.text_id, new_x + node.width // 2, 
                          new_y + node.height // 2)
        
        # Ridisegna le relazioni
        self.redraw_relationships()

    def release_node(self, event):
        """Rilascia il nodo trascinato"""
        self.dragged_node = None

    def delete_selected_nodes(self):
        """Elimina i nodi selezionati e le loro relazioni"""
        if not self.selected_nodes:
            messagebox.showwarning("Selezione vuota", "Seleziona almeno un nodo da eliminare.")
            return
        
        nodes_to_delete = self.selected_nodes.copy()
        
        for node in nodes_to_delete:
            # Trova e rimuovi tutte le relazioni che coinvolgono questo nodo
            relationships_to_remove = [
                rel for rel in self.relationships 
                if rel.src_node_id == node.id or rel.dst_node_id == node.id
            ]
            
            for rel in relationships_to_remove:
                self._remove_relationship_from_canvas(rel)
                self.relationships.remove(rel)
            
            # Rimuovi gli elementi canvas del nodo
            self.canvas.delete(node.canvas_id)
            self.canvas.delete(node.text_id)
            
            # Rimuovi il nodo dalla lista
            self.nodes.remove(node)
        
        self.selected_nodes.clear()

    def add_relationship(self):
        """Aggiunge una relazione tra nodi selezionati"""
        if len(self.selected_nodes) != 2:
            messagebox.showwarning("Selezione invalida", 
                                 "Seleziona esattamente 2 nodi per creare una relazione.")
            return

        src_node = self.selected_nodes[0]
        dst_node = self.selected_nodes[1]

        # Verifica che non esista già una relazione identica
        if self._relationship_exists(src_node, dst_node):
            messagebox.showwarning("Relazione esistente", 
                                 "Esiste già una relazione tra questi nodi.")
            return

        # Finestra di dialogo per definire la relazione
        self._show_relationship_dialog(src_node, dst_node)

    def _relationship_exists(self, src_node, dst_node):
        """Verifica se esiste già una relazione tra due nodi"""
        return any(
            rel.src_node_id == src_node.id and rel.dst_node_id == dst_node.id
            for rel in self.relationships
        )

    def _show_relationship_dialog(self, src_node, dst_node):
        """Mostra il dialogo per definire una relazione"""
        rel_window = ctk.CTkToplevel(self)
        rel_window.title("Definisci Relazione")
        rel_window.geometry("450x350")
        rel_window.grab_set()

        # Variabili
        rel_type_var = tk.StringVar(value="ordered")
        condition_var = tk.StringVar()

        # UI
        ctk.CTkLabel(rel_window, text=f"Da: {src_node.service.name}").pack(pady=5)
        ctk.CTkLabel(rel_window, text=f"A: {dst_node.service.name}").pack(pady=5)
        
        ctk.CTkLabel(rel_window, text="Tipo Relazione:").pack(pady=5)
        type_menu = ctk.CTkOptionMenu(
            rel_window, 
            variable=rel_type_var,
            values=["ordered", "on-success", "condition"]
        )
        type_menu.pack(pady=5)

        # Frame condizione (nascosto inizialmente)
        cond_frame = ctk.CTkFrame(rel_window)
        ctk.CTkLabel(cond_frame, text="Condizione:").pack(side="left", padx=5)
        cond_entry = ctk.CTkEntry(cond_frame, textvariable=condition_var, width=200)
        cond_entry.pack(side="right", padx=5)

        def on_type_change(*args):
            if rel_type_var.get() == "condition":
                cond_frame.pack(pady=10)
            else:
                cond_frame.pack_forget()

        rel_type_var.trace("w", on_type_change)

        def confirm_relationship():
            rel_type = rel_type_var.get()
            condition = condition_var.get().strip() if rel_type == "condition" else None

            if rel_type == "condition" and not condition:
                messagebox.showerror("Errore", "Inserisci una condizione valida.")
                return

            if (rel_type == "condition" and condition and 
                not any(condition.startswith(op) for op in ["<", ">", "=", "<=", ">=", "!="])):
                messagebox.showerror("Errore", 
                                   "La condizione deve iniziare con uno tra <, >, =, <=, >=, !=")
                return

            # Crea l'oggetto Relationship del modello
            relationship_obj = Relationship(
                name=f"{src_node.service.name}_to_{dst_node.service.name}_{rel_type}_{self.relationship_creation_counter}",
                category=self._get_relationship_category(rel_type),
                type=rel_type,
                description=condition if condition else rel_type,
                src=src_node.service,
                dst=dst_node.service,
                condition=condition
            )

            # Crea RelationshipGraph
            rel_graph = RelationshipGraph(src_node, dst_node, rel_type, condition, relationship_obj)
            rel_graph.creation_order = self.relationship_creation_counter
            self.relationship_creation_counter += 1

            # Aggiungi alla lista
            self.relationships.append(rel_graph)

            # Disegna la relazione
            self._draw_relationship(rel_graph)

            # Chiudi finestra e deseleziona nodi
            rel_window.destroy()
            self._deselect_all_nodes()

        ctk.CTkButton(rel_window, text="Conferma", command=confirm_relationship).pack(pady=20)

    def _get_relationship_category(self, rel_type):
        """Restituisce la categoria della relazione basata sul tipo"""
        category_map = {
            "ordered": "order",
            "on-success": "order-based",
            "condition": "conditional"
        }
        return category_map.get(rel_type, "order")

    def _draw_relationship(self, rel_graph):
        """Disegna una relazione sul canvas"""
        src_node = self.find_node_by_id(rel_graph.src_node_id)
        dst_node = self.find_node_by_id(rel_graph.dst_node_id)
        
        if not src_node or not dst_node:
            return

        line_id, label_pos = self.calculate_arrow_path(src_node, dst_node, rel_graph.color)
        rel_graph.line_id = line_id

        # Aggiungi etichetta condizione se necessaria
        if rel_graph.condition:
            label_id = self.canvas.create_text(
                label_pos[0], label_pos[1],
                text=rel_graph.condition,
                fill=rel_graph.color,
                font=("Arial", 9, "italic"),
                anchor="w"
            )
            rel_graph.condition_label_id = label_id

    def _remove_relationship_from_canvas(self, rel_graph):
        """Rimuove una relazione dal canvas"""
        if rel_graph.line_id:
            self.canvas.delete(rel_graph.line_id)
        if rel_graph.condition_label_id:
            self.canvas.delete(rel_graph.condition_label_id)

    def _deselect_all_nodes(self):
        """Deseleziona tutti i nodi"""
        for node in self.selected_nodes:
            node.is_selected = False
            self.canvas.itemconfig(node.canvas_id, outline="black", width=1)
        self.selected_nodes.clear()

    def redraw_relationships(self):
        """Ridisegna tutte le relazioni"""
        for rel_graph in self.relationships:
            # Rimuovi elementi esistenti
            self._remove_relationship_from_canvas(rel_graph)
            # Ridisegna
            self._draw_relationship(rel_graph)

    def calculate_arrow_path(self, src_node, dst_node, color):
        """Calcola il percorso della freccia tra due nodi"""
        src_idx = self.nodes.index(src_node) if src_node in self.nodes else -1
        dst_idx = self.nodes.index(dst_node) if dst_node in self.nodes else -1
        
        distance = abs(dst_idx - src_idx) if src_idx != -1 and dst_idx != -1 else 0
        vertical_distance = abs(src_node.y - dst_node.y)
        nodes_between = vertical_distance // self.NODE_SPACING

        src_x, src_y = src_node.get_bottom_center()
        dst_x, dst_y = dst_node.get_top_center()

        if distance > 1 and nodes_between > 1:
            return self.create_curved_arrow(src_node, dst_node, src_idx, dst_idx, color)
        else:
            return self.create_straight_arrow(src_x, src_y, dst_x, dst_y, color)

    def create_straight_arrow(self, src_x, src_y, dst_x, dst_y, color):
        """Crea una freccia dritta"""
        line = self.canvas.create_line(
            src_x, src_y, dst_x, dst_y,
            arrow=tk.LAST, fill=color, width=3, smooth=True
        )
        return line, (dst_x + 10, (src_y + dst_y) // 2)

    def create_curved_arrow(self, src_node, dst_node, src_idx, dst_idx, color):
        """Crea una freccia curva"""
        src_x, src_y = src_node.get_bottom_center()
        dst_x, dst_y = dst_node.get_top_center()
        
        curve_direction = 1 if (src_idx + dst_idx) % 2 == 0 else -1
        distance = abs(dst_idx - src_idx)
        lateral_offset = min(120 + (distance - 2) * 30, 200)
        
        control_x = src_x + (lateral_offset * curve_direction)
        control_y = (src_y + dst_y) // 2

        points = [
            src_x, src_y,
            src_x, src_y + 40,
            control_x, control_y - 50,
            control_x, control_y,
            control_x, control_y + 50,
            dst_x, dst_y - 40,
            dst_x, dst_y
        ]

        line = self.canvas.create_line(
            *points,
            arrow=tk.LAST, fill=color, width=3,
            smooth=True, splinesteps=30
        )

        return line, (control_x + 20, control_y)

    def sort_relationships_by_position(self):
        """Ordina le relazioni basandosi sulla posizione Y dei nodi di destinazione"""
        def get_dst_node_y(rel_graph):
            dst_node = self.find_node_by_id(rel_graph.dst_node_id)
            return dst_node.y if dst_node else float('inf')

        self.relationships.sort(key=get_dst_node_y)
        self.redraw_relationships()
        
        messagebox.showinfo("Ordinamento Completato", 
                           f"Le {len(self.relationships)} relazioni sono state ordinate "
                           "in base alla posizione dei nodi di destinazione nel canvas.")

    def show_relationship_order_preview(self):
        """Mostra l'anteprima dell'ordine delle relazioni"""
        if not self.relationships:
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

            for i, rel_graph in enumerate(self.relationships, 1):
                src_node = self.find_node_by_id(rel_graph.src_node_id)
                dst_node = self.find_node_by_id(rel_graph.dst_node_id)
                
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
        if not self.nodes:
            messagebox.showwarning("App vuota", "Aggiungi almeno un servizio prima di finalizzare.")
            return

        if self.relationships:
            result = messagebox.askyesnocancel(
                "Ordinamento Relazioni", 
                "Vuoi ordinare le relazioni in base alla posizione dei nodi prima di finalizzare?"
            )

            if result is None:
                return
            elif result:
                self.sort_relationships_by_position()

        services = [node.service for node in self.nodes]
        relationship_objects = [rel.relationship_obj for rel in self.relationships]

        if self.existing_app:
            app = IoTApp.from_data(self.existing_app.name, services, relationship_objects)
        else:
            name = simpledialog.askstring("Nome App", "Inserisci nome per l'app:")
            if not name:
                return
            app = IoTApp.from_data(name, services, relationship_objects)

        self.on_finalize(app)
        self.destroy()


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
        for i, existing_app in enumerate(apps):
            if existing_app.name == app.name:
                apps[i] = app
                break
        else:
            apps.append(app)
        apps_listbox.selection_clear(0, tk.END)
        update_apps_list()


    def update_apps_list():
        apps_listbox.delete(0, tk.END)
        for app in apps:
            apps_listbox.insert(tk.END, app.name)

    def upload_app():
        messagebox.showinfo("Upload", "This would open a file dialog to load an app.")
        GraphicalAppEditor(master, context, on_finalize_app)

    def start_new_app():
        GraphicalAppEditor(master, context, on_finalize_app, existing_app=None)

    def show_app_details(event):
        selection = apps_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        app = apps[index]
        selected_app[0] = app  # Save reference to selected app
        detail_text.delete(1.0, tk.END)
        detail_text.insert(tk.END, "📄 Human-Readable Representation:\n\n")
        detail_text.insert(tk.END, app.__repr__())
        edit_button.pack(side=tk.LEFT, padx=10)  # Show the edit button

    def edit_selected_app():
        if selected_app[0]:
            GraphicalAppEditor(master, context, on_finalize_app, existing_app=selected_app[0])

    apps_listbox.bind("<<ListboxSelect>>", show_app_details)

    buttons_frame = tk.Frame(frame, bg="#f0f0f0")
    buttons_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    ttk.Button(buttons_frame, text="📂 Upload Existing App", command=upload_app).pack(side=tk.LEFT, padx=10)
    ttk.Button(buttons_frame, text="✨ Start New App", command=start_new_app).pack(side=tk.LEFT, padx=10)

    # Bottone "Edit App" inizialmente nascosto
    edit_button = ttk.Button(buttons_frame, text="✏️ Edit App", command=edit_selected_app)

    return frame
