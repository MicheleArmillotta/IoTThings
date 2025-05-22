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
class Thing:
    id: str
    name: str
    ip: str
    port: int
    space_id: str
    type: str
    owner: str
    vendor: str
    description: str
    services: List[Service] = field(default_factory=list)

@dataclass
class Relationship:
    thing_id: str
    space_id: str
    name: str
    owner: str
    category: str
    type: str
    description: str
    src: str
    dst: str
    condition: Optional[str] = None

class IoTContext:
    def __init__(self):
        self.things: Dict[str, Thing] = {}
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

    def add_thing(self, thing_id: str, name: str, space_id: str, type_: str, owner: str, vendor: str, description: str):
        if thing_id not in self.things:
            self.things[thing_id] = Thing(name=name, ip="", port=0, id=thing_id, space_id=space_id, type=type_, owner=owner, vendor=vendor, description=description)

    def add_service_to_thing(self, thing_id: str, service_name: str, entity_id: str, space_id: str, api: str, type_: str, app_category: str, description: str, keywords: str):
        if thing_id in self.things:
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
            self.things[thing_id].services.append(service)

    def add_relationship(self, thing_id: str, space_id: str, name: str, owner: str, category: str, type_: str, description: str, fs_name: str, ss_name: str):
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
