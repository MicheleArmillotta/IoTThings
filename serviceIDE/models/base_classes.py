from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import socket
import uuid
import re

@dataclass
class Service:
    """Rappresenta un servizio base dal sistema IoT"""
    name: str
    thing_name: str
    entity_id: str
    space_id: str
    endpoint: str  # Estratto dall'API - es. "CheckFlameStatus"
    input_params: Dict[str, str] = field(default_factory=dict)  # nome_param -> tipo
    output_name: Optional[str] = None
    output_type: Optional[str] = None
    type: str = ""
    app_category: str = ""
    description: str = ""
    keywords: str = ""

    @classmethod
    def from_api_string(cls, name, thing_name, entity_id, space_id, api_string, 
                       type_="", app_category="", description="", keywords=""):
        """Crea un Service parsando l'API string originale"""
        # Parse: "CheckFlameStatus:[NULL]:(flameStatus,int,NULL)"
        match = re.match(r'^(\w+):\[(.*?)\]:\((.*?)\)$', api_string.strip())
        if not match:
            raise ValueError(f"Invalid API format: {api_string}")

        endpoint = match.group(1)
        input_str = match.group(2)
        output_str = match.group(3)

        # Parse input parameters
        input_params = {}
        if input_str.strip() and input_str.upper() != "NULL":
            for param in input_str.split('|'):
                parts = param.strip().strip('"').split(',')
                if len(parts) >= 2:
                    param_name = parts[0].strip().strip('"')
                    param_type = parts[1].strip()
                    input_params[param_name] = param_type

        # Parse output
        output_name = None
        output_type = None
        if output_str.strip() and output_str.upper() != "NULL":
            output_parts = output_str.strip().strip('"').split(',')
            if len(output_parts) >= 2:
                output_name = output_parts[0].strip()
                output_type = output_parts[1].strip()

        return cls(
            name=name,
            thing_name=thing_name,
            entity_id=entity_id,
            space_id=space_id,
            endpoint=endpoint,
            input_params=input_params,
            output_name=output_name,
            output_type=output_type,
            type=type_,
            app_category=app_category,
            description=description,
            keywords=keywords
        )

    def requires_input(self) -> bool:
        """Verifica se il servizio richiede input"""
        return len(self.input_params) > 0

    def to_api_string(self) -> str:
        """Ricostruisce l'API string originale per compatibilità"""
        input_part = "NULL"
        if self.input_params:
            params = []
            for name, type_ in self.input_params.items():
                params.append(f'"{name}",{type_},"NULL"')
            input_part = "|".join(params)

        output_part = "NULL"
        if self.output_name and self.output_type:
            output_part = f'"{self.output_name}",{self.output_type},"NULL"'

        return f"{self.endpoint}:[{input_part}]:({output_part})"
    
@dataclass
class Entity:
    thing_name: str
    space_id: str
    name: str
    entity_id: str
    type: str
    owner: str
    vendor: str
    description: str
    services: List[Service] = field(default_factory=list)

@dataclass
class Thing:
    id: str
    address: str
    name: str
    space_id: str
    model: str
    owner: str
    vendor: str
    description: str
    entities: List[Entity] = field(default_factory=list)

@dataclass
class Relationship:
    name: str
    category: str
    type: str
    description: str
    src: str
    dst: str
    thing_id: Optional[str] = None
    space_id: Optional[str] = None
    owner: Optional[str] = None
    condition: Optional[str] = None

class IoTContext:
    def __init__(self):
        self.things: Dict[str, Thing] = {}
        self.relationships: List[Relationship] = []
        self.local_ip = self._get_local_ip()
        
    @staticmethod
    def _get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def add_thing(self, thing_id: str, address: str, name: str, space_id: str, 
                  model: str, owner: str, vendor: str, description: str):
        """Aggiunge un thing solo se non esiste già"""
        if thing_id not in self.things:
            self.things[thing_id] = Thing(
                name=name, 
                address=address,
                id=thing_id, 
                space_id=space_id, 
                model=model, 
                owner=owner, 
                vendor=vendor, 
                description=description
            )

    def add_service_to_entity(self, thing_id: str, service_name: str, entity_id: str, 
                             space_id: str, api: str, type_: str, app_category: str, 
                             description: str, keywords: str):
        """Aggiunge un servizio a un'entità usando il nuovo formato Service"""
        if thing_id in self.things:
            entity_found = None
            for entity in self.things[thing_id].entities:
                if entity.entity_id == entity_id:
                    entity_found = entity
                    break
            
            if entity_found:
                # Verifica se il servizio esiste già
                service_exists = any(
                    service.name == service_name and 
                    service.entity_id == entity_id and 
                    service.thing_name == self.things[thing_id].id and
                    service.endpoint == Service.from_api_string(
                        name=service_name,
                        thing_name=self.things[thing_id].id,
                        entity_id=entity_id,
                        space_id=space_id,
                        api_string=api
                    ).endpoint
                    for service in entity_found.services
                )
                
                if not service_exists:
                    try:
                        service = Service.from_api_string(
                            name=service_name,
                            thing_name=self.things[thing_id].id,
                            entity_id=entity_id,
                            space_id=space_id,
                            api_string=api,
                            type_=type_,
                            app_category=app_category,
                            description=description,
                            keywords=keywords
                        )
                        entity_found.services.append(service)
                    except ValueError as e:
                        print(f"[Context] Error parsing API string '{api}': {e}")

    def add_entity_to_thing(self, thing_id: str, entity_name: str, entity_id: str, 
                           space_id: str, type_: str, vendor: str, description: str, owner: str):
        """Aggiunge un'entità a un thing solo se non esiste già"""
        if thing_id in self.things:
            entity_exists = any(entity.entity_id == entity_id for entity in self.things[thing_id].entities)
            
            if not entity_exists:
                entity = Entity(
                    name=entity_name,
                    thing_name=self.things[thing_id].name,
                    entity_id=entity_id,
                    space_id=space_id,
                    vendor=vendor,
                    type=type_,
                    owner=owner,
                    description=description,
                )
                self.things[thing_id].entities.append(entity)

    def add_relationship(self, thing_id: str, space_id: str, name: str, owner: str, 
                        category: str, type_: str, description: str, fs_name: str, ss_name: str):
        """Aggiunge una relazione legacy"""
        relationship_exists = any(
            rel.thing_id == thing_id and 
            rel.name == name and 
            rel.src == fs_name and 
            rel.dst == ss_name
            for rel in self.relationships
        )
        
        if not relationship_exists:
            rel = Relationship(
                type=type_,
                src=fs_name,
                dst=ss_name,
                condition=None,
                thing_id=thing_id,
                space_id=space_id,
                name=name,
                owner=owner,
                category=category,
                description=description
            )
            self.relationships.append(rel)

    def get_things(self):
        return list(self.things.values())

    def get_entities(self):
        entities = []
        for thing in self.get_things():
            for e in thing.entities:
                entities.append(e)
        return entities

    def get_services(self):
        all_services = []
        for entity in self.get_entities():
            for s in entity.services:
                all_services.append(s)
        return all_services

    def get_relationships(self):
        return self.relationships
  