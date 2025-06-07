
import json
from models.base_classes import IoTContext

def process_tweet(tweet_data: dict, addr,context: IoTContext):
    try:
        tweet_type = tweet_data.get("Tweet Type")

        if tweet_type == "Identity_Thing":
            context.add_thing(
                thing_id=tweet_data["Thing ID"],
                address = addr,
                name=tweet_data["Name"],
                space_id=tweet_data["Space ID"],
                model=tweet_data.get("Model", ""),
                owner=tweet_data.get("Owner", ""),
                vendor=tweet_data.get("Vendor", ""),
                description=tweet_data.get("Description", "")
            )
            
        elif tweet_type == "Identity_Entity":
            context.add_entity_to_thing(
                thing_id=tweet_data["Thing ID"],
                entity_name=tweet_data["Name"],
                entity_id=tweet_data["ID"],
                space_id=tweet_data["Space ID"],
                type_=tweet_data.get("Type",""),
                vendor=tweet_data.get("Vendor", ""),
                description=tweet_data.get("Description", ""),
                owner=tweet_data.get("Owner", "")
            )

        elif tweet_type == "Service":
            context.add_service_to_entity(
                thing_id=tweet_data["Thing ID"],
                service_name=tweet_data["Name"],
                entity_id=tweet_data["Entity ID"],
                space_id=tweet_data["Space ID"],
                api=tweet_data["API"],
                ip= addr[0],
                type_=tweet_data.get("Type",""),
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


