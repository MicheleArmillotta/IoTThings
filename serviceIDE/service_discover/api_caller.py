# api_caller.py

import socket
import operator
import re
from typing import Any

# 🔍 Estrae IP e porta dalla stringa API: es. "ActivateBuzzer:[NULL]:(buzzerStatus,int, NULL)"
def parse_api_string(api_str: str):
    # Questo metodo può essere migliorato se hai un formato più preciso
    # Qui supponiamo che IP e porta siano noti staticamente oppure configurabili altrove
    return api_str  # restituiamo la stringa per chiamata

# 🧠 Valuta condizione tipo: "> 5", "== 1", "<= 100"
def evaluate_condition(response: Any, condition: str) -> bool:
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        "<=": operator.le
    }

    pattern = r"(>=|<=|==|!=|>|<)\s*(\d+)"
    match = re.match(pattern, condition.strip())

    if not match:
        print(f"[ERROR] Condition malformed: '{condition}'")
        return False

    op_str, value = match.groups()
    value = int(value)

    try:
        return ops[op_str](response, value)
    except Exception as e:
        print(f"[ERROR] Evaluating condition: {e}")
        return False


import json
import socket

def call_api(service):
    print(f"[API] Calling service: {service.name} with API: {service.api}")
    
    IP = "232.1.1.1"  # Sostituisci con l’IP reale del servizio sulla tua LAN
    PORT = 1235

    if service.inputs is not None:
        service_inputs = service.inputs # -> da mettere come una lista di stringhe tra parentesi

    message = {
        "Tweet Type": "Service Call",
        "Thing id": service.thing_name,
        "Space ID": service.space_id,
        "Service Name": service.name,
        "Service Inputs": service_inputs
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(json.dumps(message).encode(), (IP, PORT))
            s.settimeout(2.0)
            data, _ = s.recvfrom(1024)
            response = data.decode().strip()
            print(f"[API RESPONSE] {response}")
            try:
                return int(response)
            except:
                return response
    except socket.timeout:
        print(f"[ERROR] Timeout calling {service.name}")
        return None
    except Exception as e:
        print(f"[ERROR] Calling {service.name}: {e}")
        return None


# 🧠 Invoca i servizi secondo le relazioni
def invoke_iot_app(app):
    print(f"[APP] Invoking IoT App: {app.name}")

    service_map = {s.name: s for s in app.services}

    for rel in app.relationships:
        
        src = rel.src
        dst = rel.dst
        rel_type = rel.type.lower()
        print(f"[DEBUG] rel.src: {rel.src} ({type(rel.src)}), rel.dst: {rel.dst} ({type(rel.dst)})")

        src_service = service_map.get(src)
        dst_service = service_map.get(dst)

        if not src_service or not dst_service:
            print(f"[WARNING] Missing service(s): {src} or {dst}")
            continue

        if rel_type == "ordered":
            call_api(src_service)
            call_api(dst_service)

        elif rel_type == "on-success":
            res = call_api(src_service)
            if res is not None:
                print(f"[SUCCESS] {src} completed. Running {dst}")
                call_api(dst_service)

        elif rel_type == "condition":
            response = call_api(src_service)
            if response is not None and rel.condition:
                if evaluate_condition(response, rel.condition):
                    print(f"[CONDITION TRUE] {rel.condition} satisfied. Running {dst}")
                    call_api(dst_service)
                else:
                    print(f"[CONDITION FALSE] {rel.condition} not satisfied. Skipping {dst}")
        else:
            print(f"[WARNING] Unknown relation type: {rel.type}")
