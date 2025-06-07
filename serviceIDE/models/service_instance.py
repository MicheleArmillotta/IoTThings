
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import uuid
import re 
from models.base_classes import Service

@dataclass
class ServiceInstance:
    """Rappresenta un'istanza specifica di un servizio in un'applicazione"""
    id: str
    service: Service
    input_values: Dict[str, str] = field(default_factory=dict)  # nome_param -> valore
    custom_name: Optional[str] = None  # Nome personalizzato per questa istanza

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_from_service(cls, service: Service, custom_name: Optional[str] = None):
        """Factory method per creare un ServiceInstance da un Service"""
        return cls(
            id=str(uuid.uuid4()),
            service=service,
            custom_name=custom_name
        )
  

    def get_display_name(self) -> str:
        """Restituisce il nome da mostrare nell'interfaccia"""
        if self.custom_name:
            return self.custom_name
        return self.service.name

    def has_configured_inputs(self) -> bool:
        """Verifica se tutti gli input richiesti sono configurati"""
        required_inputs = set(self.service.input_params.keys())
        configured_inputs = set(self.input_values.keys())
        return required_inputs.issubset(configured_inputs)

    def get_missing_inputs(self) -> List[str]:
        """Restituisce la lista degli input mancanti"""
        required = set(self.service.input_params.keys())
        configured = set(self.input_values.keys())
        return list(required - configured)

    def validate_input_value(self, param_name: str, value: str) -> bool:
        """Valida un valore di input"""
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
            # str è sempre valido
            return True
        except ValueError:
            return False

    def to_dict(self) -> Dict:
        """Serializza in dizionario"""
        return {
            "id": self.id,
            "service": self.service.__dict__,
            "input_values": self.input_values,
            "custom_name": self.custom_name
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Deserializza da dizionario"""
        service_data = data["service"]
        service = Service(**service_data)
        
        return cls(
            id=data["id"],
            service=service,
            input_values=data.get("input_values", {}),
            custom_name=data.get("custom_name")
        )
