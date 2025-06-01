# gui/components/node_graph.py
import uuid

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