import socket
import json
import time
import random

MULTICAST_GROUP = '232.1.1.1'
PORT = 1235
TWEET_INTERVAL = 120  # seconds

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1) #LOCAL TESTING

def send_tweet(tweet_dict):
    message = json.dumps(tweet_dict)
    print(f"Announcing tweet: {message}\n")
    sock.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))

def send_atlas_tweets():
    print("Your Atlas thing started to announce the tweets to the smart space through IP Socket multicasting ....")

    tweets = [
        {
            "Tweet Type": "Identity_Thing", "Thing ID": "MySmartThing01", "Space ID": "MySmartSpace",
            "Name": "RaspberrryPi", "Model": "4B", "Vendor": "RaspberryPiCo", "Owner": "IoTLab",
            "Description": "", "OS": "Raspbian"
        },
        {
            "Tweet Type": "Identity_Language", "Thing ID": "MySmartThing01", "Space ID": "MySmartSpace",
            "Network Name": "GL-SFT1200-300", "Communication Language": "Sockets", "IP": "0.0.0.0", "Port": "6668"
        },
        {
            "Tweet Type": "Identity_Entity", "Thing ID": "MySmartThing01", "Space ID": "MySmartSpace",
            "Name": "FlameAlarm", "ID": "FlameAlarm01", "Type": "Connected", "Owner": "", "Vendor": "",
            "Description": "Flame sensor and buzzer"
        },
        {
            "Tweet Type": "Service", "Name": "CheckFlameStatus", "Thing ID": "MySmartThing01", "Entity ID": "FlameAlarm01",
            "Space ID": "MySmartSpace", "Vendor": "", "API": "CheckFlameStatus:[NULL]:(flameStatus,int, NULL)",
            "Type": "Report", "AppCategory": "Safety", "Description": "flame sensor", "Keywords": "flame,sensor,monitoring"
        },
        {
            "Tweet Type": "Service", "Name": "ActivateBuzzer", "Thing ID": "MySmartThing01", "Entity ID": "FlameAlarm01",
            "Space ID": "MySmartSpace", "Vendor": "", "API": "ActivateBuzzer:[NULL]:(buzzerStatus,int, NULL)",
            "Type": "Action", "AppCategory": "Time Alarms", "Description": "buzzer", "Keywords": "noise"
        },
        {
            "Tweet Type": "Relationship", "Thing ID": "MySmartThing01", "Space ID": "MySmartSpace",
            "Name": "flameBuzz", "Owner": "", "Category": "Cooperative", "Type": "control",
            "Description": "it permit to activate the buzzer after the detection of a flame",
            "FS name": "CheckFlameStatus", "SS name": "ActivateBuzzer"
        }
    ]

    for tweet in tweets:
        send_tweet(tweet)

    print("Your Atlas thing is now ready to accept calls for the offered services ....\n")

def generate_other_device_tweets():
    # Random ID to simulate dynamic behavior
    suffix = str(random.randint(100, 999))
    thing_id = f"MyOtherThing{suffix}"
    entity_id = f"TempSensor{suffix}"

    tweets = [
        {
            "Tweet Type": "Identity_Thing", "Thing ID": thing_id, "Space ID": "MySmartSpace",
            "Name": "RaspberryPiZero", "Model": "ZeroW", "Vendor": "RaspberryPiCo", "Owner": "TestLab",
            "Description": "Secondary sensor unit", "OS": "Raspbian Lite"
        },
        {
            "Tweet Type": "Identity_Language", "Thing ID": thing_id, "Space ID": "MySmartSpace",
            "Network Name": "GuestNet", "Communication Language": "Sockets", "IP": "0.0.0.0", "Port": str(6000 + int(suffix))
        },
        {
            "Tweet Type": "Identity_Entity", "Thing ID": thing_id, "Space ID": "MySmartSpace",
            "Name": "TemperatureSensor", "ID": entity_id, "Type": "Sensor", "Owner": "", "Vendor": "",
            "Description": "Temp sensor"
        },
        {
            "Tweet Type": "Service", "Name": "GetTemperature", "Thing ID": thing_id, "Entity ID": entity_id,
            "Space ID": "MySmartSpace", "Vendor": "", "API": "GetTemperature:[NULL]:(temperature,float,NULL)",
            "Type": "Report", "AppCategory": "Environment", "Description": "Reads temperature", "Keywords": "temperature,monitoring"
        },
        {
            "Tweet Type": "Service", "Name": "CalibrateSensor", "Thing ID": thing_id, "Entity ID": entity_id,
            "Space ID": "MySmartSpace", "Vendor": "", "API": "CalibrateSensor:[NULL]:(status,bool,NULL)",
            "Type": "Action", "AppCategory": "Maintenance", "Description": "Recalibrate sensor", "Keywords": "calibration,temp"
        },
        {
            "Tweet Type": "Relationship", "Thing ID": thing_id, "Space ID": "MySmartSpace",
            "Name": "TempControl", "Owner": "", "Category": "Assistive", "Type": "regulate",
            "Description": "Triggers calibration if out of range", "FS name": "GetTemperature", "SS name": "CalibrateSensor"
        }
    ]

    for tweet in tweets:
        send_tweet(tweet)

def main_loop():
    while True:
        send_atlas_tweets()
        generate_other_device_tweets()
        print(f"--- Waiting {TWEET_INTERVAL} seconds for next cycle ---\n")
        time.sleep(TWEET_INTERVAL)

if __name__ == "__main__":
    main_loop()
