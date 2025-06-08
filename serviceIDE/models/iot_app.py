from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import uuid
from models.base_classes import Service
from models.service_instance import ServiceInstance
from models.relationship_instance import RelationshipInstance

class IoTApp:
    def __init__(self, name: str, id: str = None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.service_instances: List[ServiceInstance] = []
        self.relationship_instances: List[RelationshipInstance] = []

    def add_service_instance(self, service_instance: ServiceInstance):
        """Adds a ServiceInstance to the app"""
        if service_instance not in self.service_instances:
            self.service_instances.append(service_instance)

    def remove_service_instance(self, service_instance_id: str):
        """Removes a ServiceInstance and all its relationships"""
        # Remove associated relationships
        self.relationship_instances = [
            rel for rel in self.relationship_instances
            if rel.src_service_instance.id != service_instance_id and 
               rel.dst_service_instance.id != service_instance_id
        ]
        
        # Remove the service instance
        self.service_instances = [
            si for si in self.service_instances 
            if si.id != service_instance_id
        ]

    def add_relationship_instance(self, relationship_instance: RelationshipInstance):
        """Adds a RelationshipInstance to the app"""
        # Verify that both ServiceInstances are in the app
        src_exists = any(si.id == relationship_instance.get_src_id()
                        for si in self.service_instances)
        dst_exists = any(si.id == relationship_instance.get_dst_id() 
                        for si in self.service_instances)
        
        if not src_exists or not dst_exists:
            raise ValueError("Both ServiceInstances must be in the app before adding the relationship")
        
        self.relationship_instances.append(relationship_instance)

    def get_service_instance_by_id(self, service_id: str) -> Optional[ServiceInstance]:
        """Finds a ServiceInstance by ID"""
        for si in self.service_instances:
            if si.id == service_id:
                return si
        return None

    def get_duplicate_services(self) -> Dict[str, List[ServiceInstance]]:
        """Groups ServiceInstances by base service"""
        groups = {}
        for si in self.service_instances:
            service_key = f"{si.service.name}_{si.service.entity_id}"
            if service_key not in groups:
                groups[service_key] = []
            groups[service_key].append(si)
        return {k: v for k, v in groups.items() if len(v) > 1}

    def validate_app(self) -> List[str]:
        """Validates the app and returns a list of errors"""
        errors = []
        
        # Verify that there are service instances
        if not self.service_instances:
            errors.append("App must have at least one service instance")
        
        # Verify that all ServiceInstances have configured inputs if required
        for si in self.service_instances:
            missing_inputs = si.get_missing_inputs()
            if missing_inputs:
                errors.append(f"Service '{si.get_display_name()}' missing inputs: {', '.join(missing_inputs)}")
        
        # Verify that relationships have valid ServiceInstances
        for rel in self.relationship_instances:
            if rel.src_service_instance not in self.service_instances:
                errors.append(f"Relationship '{rel.get_display_name()}' has invalid source service")
            if rel.dst_service_instance not in self.service_instances:
                errors.append(f"Relationship '{rel.get_display_name()}' has invalid destination service")
        
        return errors

    def __repr__(self) -> str:
        lines = [f"📱 IoT Application: '{self.name}'"]
        lines.append(f"   📋 Service Instances: {len(self.service_instances)}")
        lines.append(f"   🔗 Relationships: {len(self.relationship_instances)}")

        if self.service_instances:
            lines.append("\n🔧 Service Instances:")
            for si in self.service_instances:
                status = "✅" if si.has_configured_inputs() else "⚠️"
                lines.append(f"   {status} {si.get_display_name()} ")
                if si.input_values:
                    for param, value in si.input_values.items():
                        lines.append(f"       • {param}: {value}")

        if self.relationship_instances:
            lines.append("\n🔗 Relationships:")
            for rel in self.relationship_instances:
                lines.append(f"   • {rel.get_display_name()}")

        # Show duplicates if they exist
        duplicates = self.get_duplicate_services()
        if duplicates:
            lines.append("\n👥 Duplicate Services:")
            for service_name, instances in duplicates.items():
                lines.append(f"   • {service_name}: {len(instances)} instances")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Serializes the app into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "service_instances": [si.to_dict() for si in self.service_instances],
            "relationship_instances": [ri.to_dict() for ri in self.relationship_instances]
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Deserializes the app from a dictionary"""
        app = cls(data["name"], id=data.get("id"))  # <-- Pass the id!
        
        # Load service instances
        for si_data in data.get("service_instances", []):
            si = ServiceInstance.from_dict(si_data)
            app.add_service_instance(si)
        
        # Load relationship instances
        for ri_data in data.get("relationship_instances", []):
            ri = RelationshipInstance.from_dict(ri_data)
            app.add_relationship_instance(ri)
        
        return app
    
    @classmethod
    def from_data(cls, name, services: list[ServiceInstance], relationships: list[RelationshipInstance], exist: bool, id: str = None) -> 'IoTApp':
        """
        Creates an IoTApp from a list of ServiceInstance and RelationshipInstance objects.
        The relationship list is assumed to be ordered.
        """
        app = cls(name, id=id if exist else None)
        for s in services:
            app.add_service_instance(s)
        for rel in relationships:
            app.add_relationship_instance(rel)
        return app
