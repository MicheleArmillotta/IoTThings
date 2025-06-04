# api_caller.py

import socket
import operator
import re
from typing import Any
import json

#utilizzata per capire se il metodo vuole degi input
def parse_api_string(api_str, input_names, input_types):
    match = re.match(r'^(\w+):\[(.*?)\]:\((.*?)\)$', api_str.strip())
    if not match:
        raise ValueError("Formato non valido")

    endpoint = match.group(1)
    input_str = match.group(2)
    output_str = match.group(3)

    input_names.clear()
    input_types.clear()

    for param in input_str.split('|'):
        parts = param.strip().strip('"').split(',')
        if len(parts) >= 2:
            input_names.append(parts[0].strip().strip('"'))
            input_types.append(parts[1].strip())

    output_parts = output_str.strip().strip('"').split(',')
    if len(output_parts) >= 2:
        output_name = output_parts[0].strip()
        output_type = output_parts[1].strip()
        output = (output_name, output_type)
    else:
        output = (None, None)

    return endpoint, output

def build_request(service, endpoint, input_names, input_types, write_fn, input_fn):
    inputs = ""
    if input_names and input_types:
        values = []
        for name, type_str in zip(input_names, input_types):
            while True:
                try:
                    value = input_fn(f"Inserisci il valore per '{name}' ({type_str}): ")
                    if not value:
                        write_fn("Input annullato o vuoto. Riprova.\n")
                        continue
                    if value.lower() == "null":
                        value = "null"
                    elif type_str == "int":
                        value = str(int(value))
                    elif type_str == "float":
                        value = str(float(value))
                    elif type_str == "bool":
                        value = "true" if value.lower() in ["true", "1", "sì", "si", "yes"] else "false"
                    elif type_str == "str":
                        value = f'"{value}"'
                    else:
                        write_fn(f"Tipo '{type_str}' non supportato, trattato come stringa.\n")
                        value = f'"{value}"'
                    values.append(value)
                    break
                except ValueError:
                    write_fn(f"Valore non valido per il tipo {type_str}. Riprova.\n")
        inputs = f"({', '.join(values)})"
    else:
        inputs = "()"

    request = {
        "Tweet Type": "Service Call",
        "Thing ID": service.thing_name,
        "Space ID": service.space_id,
        "Service Name": endpoint,
        "Service Inputs": inputs
    }
    return request

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
        return False
    op_str, value = match.groups()
    value = int(value)
    try:
        return ops[op_str](response, value)
    except Exception:
        return False

def call_api(service, req, write_fn):
    write_fn(f"[API] Calling service: {service.name} with API: {json.dumps(req)}\n")
    IP = '192.168.8.201'
    PORT = 6668
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10.0)
            s.connect((IP, PORT))
            s.sendall(json.dumps(req).encode('utf-8'))
            response = s.recv(4096).decode('utf-8').strip()
            write_fn(f"[API RESPONSE] {response}\n")
            return response
    except socket.timeout:
        write_fn(f"[ERROR] Timeout calling {service.name}\n")
        return None
    except Exception as e:
        write_fn(f"[ERROR] Calling {service.name}: {e}\n")
        return None

def invoke_iot_app(app, write_fn, input_fn):
    write_fn(f"[APP] Invoking IoT App: {app.name}\n")
    service_map = {s.name: s for s in app.services}
    inputs_names = []
    inputs_types = []
    res_map = {} #mappa per valutare le condizioni (fatta anche in maniera tale da non invocare più volte lo stesso servizio src dato che è sbagliato farlo {nome servzio,succes=true/false, result se c'è})

    for rel in app.relationships:
        src = rel.src
        dst = rel.dst
        rel_type = rel.type.lower()
        write_fn(f"[DEBUG] rel.src: {rel.src} ({type(rel.src)}), rel.dst: {rel.dst} ({type(rel.dst)})\n")

        src_service = service_map.get(src)
        dst_service = service_map.get(dst)

        if not src_service or not dst_service:
            write_fn(f"[WARNING] Missing service(s): {src} or {dst}\n")
            continue

        if not res_map:
            write_fn("[FIRST CALL] Executing source service\n")
            endpoint, output = parse_api_string(src_service.api, inputs_names, inputs_types)
            req = build_request(src_service, endpoint, inputs_names, inputs_types, write_fn, input_fn)
            res = call_api(src_service, req, write_fn)
            try:
                res_json = json.loads(res) if res else {}
                status = res_json.get("Status", "").lower() == "successful"
                service_result = res_json.get("Service Result", None)
            except Exception as e:
                write_fn(f"[ERROR] Parsing response for {src_service.name}: {e}\n")
                status = False
                service_result = None
            res_map[src_service.name] = [status, service_result]
            write_fn(f"[RESULT] {src_service.name}: Success={status}, Result={service_result}\n")

        should_execute_dst = False

        if rel_type == "ordered":
            write_fn(f"[ORDERED] Executing destination service: {dst}\n")
            should_execute_dst = True
        elif rel_type == "on-success":
            src_result = res_map.get(src_service.name)
            if src_result and src_result[0]:
                write_fn(f"[ON-SUCCESS] Source {src} successful. Executing destination: {dst}\n")
                should_execute_dst = True
            else:
                write_fn(f"[ON-SUCCESS] Source {src} failed. Skipping destination: {dst}\n")
        elif rel_type == "condition" or rel_type == "conditional":
            src_result = res_map.get(src_service.name)
            if src_result and src_result[0] and hasattr(rel, 'condition'):
                try:
                    response_value = int(src_result[1])
                except (ValueError, TypeError):
                    response_value = src_result[1]
                condition_result = evaluate_condition(response_value, rel.condition)
                if condition_result:
                    write_fn(f"[CONDITIONAL] Condition '{rel.condition}' satisfied. Executing destination: {dst}\n")
                    should_execute_dst = True
                else:
                    write_fn(f"[CONDITIONAL] Condition '{rel.condition}' not satisfied. Skipping destination: {dst}\n")
            else:
                write_fn(f"[CONDITIONAL] Source {src} failed or no condition. Skipping destination: {dst}\n")
        else:
            write_fn(f"[WARNING] Unknown relation type: {rel.type}\n")

        if should_execute_dst:
            inputs_names.clear()
            inputs_types.clear()
            endpoint, output = parse_api_string(dst_service.api, inputs_names, inputs_types)
            req = build_request(dst_service, endpoint, inputs_names, inputs_types, write_fn, input_fn)
            res = call_api(dst_service, req, write_fn)
            try:
                res_json = json.loads(res) if res else {}
                status = res_json.get("Status", "").lower() == "successful"
                service_result = res_json.get("Service Result", None)
            except Exception as e:
                write_fn(f"[ERROR] Parsing response for {dst_service.name}: {e}\n")
                status = False
                service_result = None
            res_map[dst_service.name] = [status, service_result]
            write_fn(f"[RESULT] {dst_service.name}: Success={status}, Result={service_result}\n")

    write_fn(f"[PROMPT] EXECUTION COMPLETED\n")
    write_fn("\n[SERVICE RESULTS SUMMARY]\n")
    for k, v in res_map.items():
        write_fn(f"{k}: Success={v[0]}, Result={v[1]}\n")
    return res_map