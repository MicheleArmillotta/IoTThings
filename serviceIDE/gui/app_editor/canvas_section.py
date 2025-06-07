# gui/components/app_canvas.py
import tkinter as tk
import math
import os
import json
from tkinter import messagebox
from gui.app_editor.node_graph import NodeGraph
from gui.app_editor.relationship_graph import RelationshipGraph
from models.service_instance import ServiceInstance


class AppCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg="white", **kwargs)

        self.nodes = []  # Lista di NodeGraph
        self.relationships = []  # Lista di RelationshipGraph

        # Variabili per il drag & drop
        self.dragged_node = None
        self.drag_offset = (0, 0)
        self.selected_nodes = []

        self._setup_bindings()

    def _setup_bindings(self):
        self.bind("<Button-1>", self._on_canvas_click)
        self.bind("<B1-Motion>", self._on_canvas_drag)
        self.bind("<ButtonRelease-1>", self._on_canvas_release)

    def _on_canvas_click(self, event):
        """Gestisce il click sul canvas (selezione nodi)"""
        clicked_items = self.find_closest(event.x, event.y)
        node = self.find_node_by_canvas_id(clicked_items[0])

        if node:
            if node in self.selected_nodes:
                # Deseleziona
                self.selected_nodes.remove(node)
                node.is_selected = False
                self.itemconfig(node.canvas_id, outline="black", width=1)
            else:
                # Seleziona
                self.selected_nodes.append(node)
                node.is_selected = True
                self.itemconfig(node.canvas_id, outline="red", width=3)
                
        if hasattr(self.master, "update_input_panel"):
            self.master.update_input_panel()

    def _on_canvas_drag(self, event):
        """Gestisce il trascinamento dei nodi"""
        if not self.dragged_node:
            clicked_items = self.find_withtag("current")
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
        self.coords(node.canvas_id, new_x, new_y,
                          new_x + node.width, new_y + node.height)
        self.coords(node.text_id, new_x + node.width // 2,
                          new_y + node.height // 2)

        # Ridisegna le relazioni
        self.redraw_relationships()

    def _on_canvas_release(self, event):
        """Rilascia il nodo trascinato"""
        self.dragged_node = None

    def add_node(self, service, x, y):
        """Aggiunge un nuovo nodo servizio al canvas e lo disegna"""
        canvas_id = self.create_oval(
            x, y, x + 100, y + 60, # Utilizza le costanti dal NodeGraph
            fill="#b3d9ff", tags="node"
        )
        text_id = self.create_text(
            x + 100 // 2, y + 60 // 2,
            text=service.get_display_name(), tags="node"
        )
        node = NodeGraph(service, x, y, canvas_id, text_id)
        self.nodes.append(node)
        return node

    def delete_node(self, node_id):
        """Elimina un nodo dal canvas e dalla lista"""
        node_to_delete = self.find_node_by_id(node_id)
        if node_to_delete:
            self.delete(node_to_delete.canvas_id)
            self.delete(node_to_delete.text_id)
            self.nodes.remove(node_to_delete)
            if node_to_delete in self.selected_nodes:
                self.selected_nodes.remove(node_to_delete)

            # Rimuovi anche le relazioni collegate a questo nodo
            relationships_to_remove = [
                rel for rel in self.relationships
                if rel.get_src_id() == node_to_delete.get_service_id() or rel.get_dst_id() == node_to_delete.get_service_id()
            ]
            for rel in relationships_to_remove:
                self._remove_relationship_from_canvas(rel)
                self.relationships.remove(rel)

    def add_relationship(self, rel_type, condition, relationship_obj, creation_order_value):
        """Aggiunge e disegna una relazione tra due nodi"""
        rel_graph = RelationshipGraph(rel_type, condition, relationship_obj)
        rel_graph.creation_order = creation_order_value
        self.relationships.append(rel_graph)
        self._draw_relationship(rel_graph)
        return rel_graph

    def _draw_relationship(self, rel_graph):
        """Disegna una relazione sul canvas"""
        src_node = self.find_node_by_id(rel_graph.get_src_id())
        dst_node = self.find_node_by_id(rel_graph.get_dst_id())

        if not src_node or not dst_node:
            return

        line_id, label_pos = self._calculate_arrow_path(src_node, dst_node, rel_graph.color)
        rel_graph.line_id = line_id

        # Aggiungi etichetta condizione se necessaria
        if rel_graph.condition:
            label_id = self.create_text(
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
            self.delete(rel_graph.line_id)
        if rel_graph.condition_label_id:
            self.delete(rel_graph.condition_label_id)

    def redraw_relationships(self):
        """Ridisegna tutte le relazioni"""
        for rel_graph in self.relationships:
            # Rimuovi elementi esistenti
            self._remove_relationship_from_canvas(rel_graph)
            # Ridisegna
            self._draw_relationship(rel_graph)

    def _calculate_arrow_path(self, src_node, dst_node, color):
        """Calcola il percorso della freccia tra due nodi"""
        # Assicurati che i nodi siano nella lista per calcolare l'indice
        try:
            src_idx = self.nodes.index(src_node)
            dst_idx = self.nodes.index(dst_node)
        except ValueError:
            # Fallback se i nodi non sono trovati (dovrebbe essere raro)
            return self._create_straight_arrow(src_node.get_bottom_center()[0], src_node.get_bottom_center()[1],
                                              dst_node.get_top_center()[0], dst_node.get_top_center()[1], color)

        distance = abs(dst_idx - src_idx)
        vertical_distance = abs(src_node.y - dst_node.y)
        nodes_between = vertical_distance // src_node.height # Approssimazione

        src_x, src_y = src_node.get_bottom_center()
        dst_x, dst_y = dst_node.get_top_center()

        if distance > 1 and nodes_between > 1:
            return self._create_curved_arrow(src_node, dst_node, src_idx, dst_idx, color)
        else:
            return self._create_straight_arrow(src_x, src_y, dst_x, dst_y, color)

    def _create_straight_arrow(self, src_x, src_y, dst_x, dst_y, color):
        """Crea una freccia dritta"""
        line = self.create_line(
            src_x, src_y, dst_x, dst_y,
            arrow=tk.LAST, fill=color, width=3, smooth=True
        )
        return line, (dst_x + 10, (src_y + dst_y) // 2)

    def _create_curved_arrow(self, src_node, dst_node, src_idx, dst_idx, color):
        """Crea una freccia curva"""
        src_x, src_y = src_node.get_bottom_center()
        dst_x, dst_y = dst_node.get_top_center()

        curve_direction = 1 if (src_idx + dst_idx) % 2 == 0 else -1
        # L'offset dipende dalla distanza tra i nodi
        lateral_offset = min(120 + abs(src_idx - dst_idx - 1) * 30, 200)

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

        line = self.create_line(
            *points,
            arrow=tk.LAST, fill=color, width=3,
            smooth=True, splinesteps=30
        )

        return line, (control_x + 20, control_y)

    def find_node_by_canvas_id(self, canvas_id):
        """Trova un nodo basandosi sull'ID dell'elemento canvas"""
        for node in self.nodes:
            if canvas_id in (node.canvas_id, node.text_id):
                return node
        return None

    def find_node_by_id(self, node_id):
        """Trova un nodo per id del NodeGraph o per id del servizio associato"""
        for node in self.nodes:
            # Cerca per id del nodo
            if node.id == node_id:
                return node
            # Cerca per id del ServiceInstance (se presente)
            if hasattr(node, "service") and hasattr(node.service, "id") and node.service.id == node_id:
                return node
            # Cerca per id del Service incapsulato (se ServiceInstance)
            if hasattr(node, "service") and hasattr(node.service, "service") and hasattr(node.service.service, "id"):
                if node.service.service.id == node_id:
                    return node
        return None

    def deselect_all_nodes(self):
        """Deseleziona tutti i nodi"""
        for node in self.selected_nodes:
            node.is_selected = False
            self.itemconfig(node.canvas_id, outline="black", width=1)
        self.selected_nodes.clear()

    def get_nodes(self):
        return self.nodes

    def get_relationships(self):
        return self.relationships

    def clear_canvas(self):
        """Cancella tutti gli elementi dal canvas"""
        self.delete("all")
        self.nodes.clear()
        self.relationships.clear()
        self.selected_nodes.clear()


    def save_graphical_app_editor(self, name):
        services = [node.service for node in self.nodes]
        relationships = [edge.relationship_obj for edge in self.relationships]
        config_path = os.path.join(os.path.dirname(__file__), "../tabs/workdir_path")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                path = f.read().strip()
                if os.path.isdir(path):
                    workdir = path

        try:
        
            filename = os.path.join(workdir, f"{name}.iot")

            if os.path.exists(filename):
                confirm = messagebox.askyesno("File Exists",
                                            f"A file named '{name}.iot' already exists.\nDo you want to overwrite it?")
                if not confirm:
                    messagebox.showinfo("Cancelled", "Save cancelled by user.")
                    return

            app_data = {
                "name": name,
                "services": [service.__dict__ for service in services],
                "relationships": [rel.__dict__ for rel in relationships]
            }

            with open(filename, "w") as f:
                json.dump(app_data, f, indent=4)

                messagebox.showinfo("Success", f"App saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save app: {e}")