from dataclasses import dataclass

@dataclass
class ServiceTweet:
    name: str
    thing_id: str
    entity_id: str
    api: str
    description: str
    keywords: str

@dataclass
class RelationshipTweet:
    thing_id: str
    name: str
    description: str
    source_service: str
    target_service: str

@dataclass
class IdentityTweet:
    thing_id: str
    space_id: str
    name: str
    id: str
    type: str
    owner: str
    vendor: str
    decription: str
