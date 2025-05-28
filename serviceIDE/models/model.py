from dataclasses import dataclass, field
from typing import Dict, List, Optional
import socket

@dataclass
class Service:
    name: str
    thing_name: str
    entity_id: str
    space_id: str
    api: str
    type: str
    app_category: str
    description: str
    keywords: str

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
        #self.things: List[Thing] = []
        self.relationships: List[Relationship] = []
        self.local_ip = self._get_local_ip()

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def add_thing(self, thing_id: str, address:str,name: str, space_id: str, model: str, owner: str, vendor: str, description: str):
        """Aggiunge un thing solo se non esiste già"""
        if thing_id not in self.things:
            self.things[thing_id] = Thing(
                name=name, 
                address = address,
                id=thing_id, 
                space_id=space_id, 
                model=model, 
                owner=owner, 
                vendor=vendor, 
                description=description
            )
            

    def add_service_to_Entity(self, thing_id: str, service_name: str, entity_id: str, space_id: str, api: str, type_: str, app_category: str, description: str, keywords: str):
        """Aggiunge un servizio a un'entità solo se non esiste già"""
        if thing_id in self.things:
            # Trova l'entità con l'entity_id corrispondente
            entity_found = None
            for entity in self.things[thing_id].entities:
                if entity.entity_id == entity_id:
                    entity_found = entity
                    break
            
            if entity_found:
                # Controlla se il servizio esiste già (stessa combinazione name + entity_id + api)
                service_exists = any(
                    service.name == service_name and 
                    service.entity_id == entity_id and 
                    service.api == api
                    for service in entity_found.services
                )
                
                if not service_exists:
                    service = Service(
                        name=service_name,
                        thing_name=self.things[thing_id].name,
                        entity_id=entity_id,
                        space_id=space_id,
                        api=api,
                        type=type_,
                        app_category=app_category,
                        description=description,
                        keywords=keywords
                    )
                    entity_found.services.append(service)
                 
    def add_entity_to_thing(self, thing_id: str, entity_name: str, entity_id: str, space_id: str, type_: str, vendor: str, description: str, owner: str):
        """Aggiunge un'entità a un thing solo se non esiste già"""
        if thing_id in self.things:
            # Controlla se l'entità esiste già (stesso entity_id)
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
              

    def add_relationship(self, thing_id: str, space_id: str, name: str, owner: str, category: str, type_: str, description: str, fs_name: str, ss_name: str):
        """Aggiunge una relazione solo se non esiste già"""
        # Controlla se la relazione esiste già (stessa combinazione thing_id + name + src + dst)
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
        
           
    """def get_entity_by_id(self, thing_id: str, entity_id: str) -> Optional[Entity]:
        #Trova un'entità specifica in base al thing_id e entity_id
        if thing_id in self.things:
            for entity in self.things[thing_id].entities:
                if entity.entity_id == entity_id:
                    return entity
        return None
       """ 
    

class IoTApp:
    def __init__(self, name):
        self.name = name
        self.services = []  # list of Service objects
        self.relationships = []  # ordered list of Relationship objects

    def add_service(self, service: Service):
        if service not in self.services:
            self.services.append(service)

    def add_relationship_obj(self, relationship: Relationship):
        if relationship.src not in self.services or relationship.dst not in self.services:
            raise ValueError("Both services must be in the app before adding the relationship.")
        self.relationships.append(relationship)

    def get_services(self):
        return self.services

    def get_relationships(self):
        return self.relationships
    
    def get_ordered_services(self):
        if not self.relationships:
            return []

        sequence = [self.relationships[0].src]
        for rel in self.relationships:
            sequence.append(rel.dst)
        return sequence


    def __repr__(self):
        lines = [f"IoTApp(name={self.name})"]
        if not self.relationships:
            lines.append("  (no relationships)")
            return "\n".join(lines)

        for rel in self.relationships:
            lines.append(f"  {rel.src.name} -[{rel.type}]-> {rel.dst.name}")
        return "\n".join(lines)

    @classmethod
    def from_data(cls, name, services: list, relationships: list):
        """
        Crea un IoTApp da una lista di oggetti Service e Relationship.
        La lista di relationship è assunta ordinata.
        """
        app = cls(name)
        for s in services:
            app.add_service(s)
        for rel in relationships:
            app.add_relationship_obj(rel)
        return app
