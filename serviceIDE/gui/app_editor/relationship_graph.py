import uuid

class RelationshipGraph:
    """Represents a relationship in the canvas with all its properties"""

    def __init__(self, rel_type, condition=None, relationship_instance=None):
        self.id = str(uuid.uuid4())  # Unique ID for the relationship
        self.type = rel_type
        self.condition = condition
        self.relationship_instance = relationship_instance  # RelationshipInstance object
        # Canvas elements
        self.line_id = None         # ID of the line in the canvas
        self.condition_label_id = None  # ID of the condition label

        # Visual properties
        self.color = self._get_color_by_type()

        # Timestamp for ordering
        self.creation_order = 0

    def _get_color_by_type(self):
        """Returns the color based on the relationship type"""
        color_map = {
            "ordered": "black",
            "on-success": "green",
            "condition": "purple"
        }
        return color_map.get(self.type, "black")

    def get_display_name(self):
        """Returns a descriptive name for the relationship"""
        base_name = f"{self.src_service.name} → {self.dst_service.name}"
        if self.condition:
            return f"{base_name} ({self.condition})"
        return f"{base_name} ({self.type})"

    def __str__(self):
        return f"RelationshipGraph(id={self.id[:8]}, {self.get_display_name()})"
    
  
    def get_src_id(self) -> str:
        """Returns the ID of the encapsulated Service in src"""
        return self.relationship_instance.get_src_id()

    def get_src_name(self) -> str:
        """Returns the name of the encapsulated Service in src"""
        return self.relationship_instance.get_src_name()

    def get_dst_id(self) -> str:
        """Returns the ID of the encapsulated Service in dst"""
        return self.relationship_instance.get_dst_id()

    def get_dst_name(self) -> str:
        """Returns the name of the encapsulated Service in dst"""
        return self.relationship_instance.get_dst_name()


