from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import socket
import uuid
from models.service_instance import ServiceInstance

@dataclass
class RelationshipInstance:
    """Represents a specific relationship between two ServiceInstances"""
    id: str
    src: ServiceInstance
    dst: ServiceInstance
    type: str  # "ordered", "on-success", "condition"
    condition: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.name:
            self.name = f"{self.src.get_display_name()}_to_{self.dst.get_display_name()}_{self.type}"
        if not self.category:
            self.category = self._get_default_category()

    def _get_default_category(self) -> str:
        """Determines the default category based on the type"""
        category_map = {
            "ordered": "order",
            "on-success": "order-based", 
            "condition": "conditional"
        }
        return category_map.get(self.type, "order")

    @classmethod
    def create(cls, src_instance: ServiceInstance, dst_instance: ServiceInstance, 
               rel_type: str, condition: Optional[str] = None):
        """Factory method to create a RelationshipInstance"""
        return cls(
            id=str(uuid.uuid4()),
            src=src_instance,
            dst=dst_instance,
            type=rel_type,
            condition=condition
        )

    def get_display_name(self) -> str:
        """Returns the name to display in the interface"""
        base_name = f"{self.src.get_display_name()} → {self.dst.get_display_name()}"
        if self.condition:
            return f"{base_name} ({self.condition})"
        return f"{base_name} ({self.type})"

    def to_dict(self) -> Dict:
        """Serializes into a dictionary"""
        return {
            "id": self.id,
            "src": self.src.to_dict(),
            "dst": self.dst.to_dict(),
            "type": self.type,
            "condition": self.condition,
            "name": self.name,
            "category": self.category,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Deserializes from a dictionary"""
        return cls(
            id=data["id"],
            src=ServiceInstance.from_dict(data["src"]),
            dst=ServiceInstance.from_dict(data["dst"]),
            type=data["type"],
            condition=data.get("condition"),
            name=data.get("name"),
            category=data.get("category"),
            description=data.get("description")
        )

    def get_src_id(self) -> str:
        """Returns the ID of the Service encapsulated in src"""
        return self.src.id

    def get_src_name(self) -> str:
        """Returns the name of the Service encapsulated in src"""
        return self.src.service.name

    def get_dst_id(self) -> str:
        """Returns the ID of the Service encapsulated in dst"""
        return self.dst.id

    def get_dst_name(self) -> str:
        """Returns the name of the Service encapsulated in dst"""
        return self.dst.service.name
