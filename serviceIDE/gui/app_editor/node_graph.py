# gui/components/node_graph.py
import uuid

class NodeGraph:
    """Represents a node on the canvas with all its properties"""

    def __init__(self, service, x, y, canvas_id=None, text_id=None):
        self.id = str(uuid.uuid4())  # Unique ID for the node
        self.service = service
        self.x = x
        self.y = y
        self.canvas_id = canvas_id  # Canvas element ID (oval)
        self.text_id = text_id      # Text ID on the canvas
        self.is_selected = False
        self.width = 100
        self.height = 60

    def get_center(self):
        """Returns the center of the node"""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def get_bottom_center(self):
        """Returns the center point of the bottom edge"""
        return (self.x + self.width // 2, self.y + self.height)

    def get_top_center(self):
        """Returns the center point of the top edge"""
        return (self.x + self.width // 2, self.y)

    def contains_point(self, x, y):
        """Checks if a point is inside the node"""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def update_position(self, new_x, new_y):
        """Updates the position of the node"""
        self.x = new_x
        self.y = new_y

    def __str__(self):
        return f"NodeGraph(id={self.id[:8]}, service={self.service.name}, pos=({self.x},{self.y}))"
    
    def get_service_id(self):
        """Returns the ID of the service encapsulated in the node"""
        return getattr(self.service, "id", None)
    
    def get_service_name(self) -> str:
        """Returns the name of the encapsulated Service"""
        return self.service.get_display_name()