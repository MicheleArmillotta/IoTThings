import uuid

class RelationshipGraph:
    """Rappresenta una relazione nel canvas con tutte le sue proprietà"""

    def __init__(self, rel_type, condition=None, relationship_instance=None):
        self.id = str(uuid.uuid4())  # ID univoco per la relazione
        self.type = rel_type
        self.condition = condition
        self.relationship_instance = relationship_instance  # Oggetto RelationshipIstance  
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
    
  
    def get_src_id(self) -> str:
        """Restituisce l'id del Service incapsulato in src"""
        return self.relationship_instance.get_src_id()

    def get_src_name(self) -> str:
        """Restituisce il nome del Service incapsulato in src"""
        return self.relationship_instance.get_src_name()

    def get_dst_id(self) -> str:
        """Restituisce l'id del Service incapsulato in dst"""
        return self.relationship_instance.get_dst_id()

    def get_dst_name(self) -> str:
        """Restituisce il nome del Service incapsulato in dst"""
        return self.relationship_instance.get_dst_name()


