from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import uuid
import re 
from models.base_classes import Service

@dataclass
class ServiceInstance:
    """Represents a specific instance of a service in an application"""
    id: str
    service: Service
    input_values: Dict[str, str] = field(default_factory=dict)  # param_name -> value
    custom_name: Optional[str] = None  # Custom name for this instance

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_from_service(cls, service: Service, custom_name: Optional[str] = None):
        """Factory method to create a ServiceInstance from a Service"""
        return cls(
            id=str(uuid.uuid4()),
            service=service,
            custom_name=custom_name
        )
  

    def get_display_name(self) -> str:
        """Returns the name to display in the interface"""
        if self.custom_name:
            return self.custom_name
        return self.service.name

    def has_configured_inputs(self) -> bool:
        """Checks if all required inputs are configured"""
        required_inputs = set(self.service.input_params.keys())
        configured_inputs = set(self.input_values.keys())
        return required_inputs.issubset(configured_inputs)

    def get_missing_inputs(self) -> List[str]:
        """Returns the list of missing inputs"""
        required = set(self.service.input_params.keys())
        configured = set(self.input_values.keys())
        return list(required - configured)

    def validate_input_value(self, param_name: str, value: str) -> bool:
        """Validates an input value"""
        if param_name not in self.service.input_params:
            return False
        
        param_type = self.service.input_params[param_name]
        
        try:
            if param_type == "int":
                int(value)
            elif param_type == "float":
                float(value)
            elif param_type == "bool":
                if value.lower() not in ["true", "false", "1", "0", "yes", "no"]:
                    return False
            # str is always valid
            return True
        except ValueError:
            return False

    def to_dict(self) -> Dict:
        """Serializes into a dictionary"""
        return {
            "id": self.id,
            "service": self.service.__dict__,
            "input_values": self.input_values,
            "custom_name": self.custom_name
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Deserializes from a dictionary"""
        service_data = data["service"]
        service = Service(**service_data)
        
        return cls(
            id=data["id"],
            service=service,
            input_values=data.get("input_values", {}),
            custom_name=data.get("custom_name")
        )
