""""
from models.tweet import ServiceTweet, RelationshipTweet, IdentityTweet

def process_tweet(data: dict):
    tweet_type = data.get("Tweet Type")

    if tweet_type == "Service":
        return ServiceTweet(
            name=data.get("Name"),
            thing_id=data.get("Thing ID"),
            entity_id=data.get("Entity ID"),
            api=data.get("API"),
            description=data.get("Description"),
            keywords=data.get("Keywords")
        )
    elif tweet_type == "Relationship":
        return RelationshipTweet(
            thing_id=data.get("Thing ID"),
            name=data.get("Name"),
            description=data.get("Description"),
            source_service=data.get("FS name"),
            target_service=data.get("SS name")
        )
    elif tweet_type == "Identity_Entity":
        return IdentityTweet(
            thing_id = data.get("Thing ID"),
            space_id = data.get("Space ID"),
            name = data.get("Name"),
            id = data.get("ID"),
            type = data.get("Type"),
            owner = data.get("Owner"),
            vendor = data.get("Vendor"),
            decription = data.get("Description")
        )

    else:
        print("[Processor] Unknown tweet type:", tweet_type)
        return None


"""""


import json
from models.model import IoTContext

def process_tweet(tweet_data: dict, context: IoTContext):
    try:
        tweet_type = tweet_data.get("Tweet Type")

        if tweet_type == "Identity_Entity":
            context.add_thing(
                thing_id=tweet_data["Thing ID"],
                name=tweet_data["Name"],
                space_id=tweet_data["Space ID"],
                type_=tweet_data["Type"],
                owner=tweet_data.get("Owner", ""),
                vendor=tweet_data.get("Vendor", ""),
                description=tweet_data.get("Description", "")
            )

        elif tweet_type == "Service":
            context.add_service_to_thing(
                thing_id=tweet_data["Thing ID"],
                service_name=tweet_data["Name"],
                entity_id=tweet_data["Entity ID"],
                space_id=tweet_data["Space ID"],
                api=tweet_data["API"],
                type_=tweet_data["Type"],
                app_category=tweet_data.get("AppCategory", ""),
                description=tweet_data.get("Description", ""),
                keywords=tweet_data.get("Keywords", "")
            )

        elif tweet_type == "Relationship":
            context.add_relationship(
                thing_id=tweet_data["Thing ID"],
                space_id=tweet_data["Space ID"],
                name=tweet_data["Name"],
                owner=tweet_data.get("Owner", ""),
                category=tweet_data.get("Category", ""),
                type_=tweet_data.get("Type", ""),
                description=tweet_data.get("Description", ""),
                fs_name=tweet_data.get("FS name", ""),
                ss_name=tweet_data.get("SS name", "")
            )

    except Exception as e:
        print(f"[Processor] Error processing tweet: {e}")


