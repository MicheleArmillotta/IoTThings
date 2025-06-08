import socket
import operator
import re
import json

def build_request(service_instance, write_fn, input_fn, src_result_map=None):
    """
    Builds the request for the service, using already configured input_values
    and, if necessary, inserting the output of the src service as input.
    """
    service = service_instance.service
    input_params = getattr(service, "input_params", {})
    input_values = dict(service_instance.input_values)  # copy to avoid modifying the original

    # If src_result_map is provided, insert the output of the src service if required
    if src_result_map:
        for param in input_params:
            if param in src_result_map:
                input_values[param] = src_result_map[param]

    # Ask the user only for missing inputs
    for param, param_type in input_params.items():
        if param not in input_values or input_values[param] == "":
            while True:
                value = input_fn(f"Enter the value for '{param}' ({param_type}): ")
                if not value:
                    write_fn("Input canceled or empty. Try again.\n")
                    continue
                try:
                    if value.lower() == "null":
                        value = "null"
                    elif param_type == "int":
                        value = str(int(value))
                    elif param_type == "float":
                        value = str(float(value))
                    elif param_type == "bool":
                        value = "true" if value.lower() in ["true", "1", "yes"] else "false"
                    elif param_type == "str":
                        value = f'"{value}"'
                    else:
                        write_fn(f"Type '{param_type}' not supported, treated as string.\n")
                        value = f'"{value}"'
                    input_values[param] = value
                    break
                except ValueError:
                    write_fn(f"Invalid value for type {param_type}. Try again.\n")

    inputs = f"({', '.join(str(input_values[p]) for p in input_params)})" if input_params else "()"

    request = {
        "Tweet Type": "Service Call",
        "Thing ID": service.thing_name,
        "Space ID": service.space_id,
        "Service Name": service.name,
        "Service Inputs": inputs
    }
    return request

def evaluate_condition(response, condition: str) -> bool:
    """
    Evaluates a condition based on the response value.
    """
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

def call_api(service_instance, req, write_fn):
    """
    Calls the API for the given service instance.
    """
    service = service_instance.service
    write_fn(f"[API] Calling service: {service.name} with API: {json.dumps(req)}\n")
    IP = service.ip
    PORT = 6668  # Hardcoded in Atlas
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

def invoke_iot_app(app, write_fn, input_fn, stop_flag=None):
    """
    Invokes the IoT application by executing its services and relationships.
    """
    write_fn(f"[APP] Invoking IoT App: {app.name}\n")
    service_map = {s.id: s for s in app.service_instances}
    res_map = {}  # id_service_instance: [success, result]
    output_map = {}  # id_service_instance: result (for auto-input)

    for rel in app.relationship_instances:
        if stop_flag and stop_flag.get("stop"):
            write_fn("[STOP] Execution interrupted by user.\n")
            break
        src_instance = rel.src
        dst_instance = rel.dst
        rel_type = rel.type.lower()
        # write_fn(f"[DEBUG] rel.src: {src_instance} ({type(src_instance)}), rel.dst: {dst_instance} ({type(dst_instance)})\n")

        src_service = service_map.get(src_instance.id)
        dst_service = service_map.get(dst_instance.id)

        if not src_service or not dst_service:
            write_fn(f"[WARNING] Missing service(s): {src_instance.get_display_name()} or {dst_instance.get_display_name()}\n")
            continue

        # Execute the source service only if not already executed
        if src_instance.id not in res_map:
            write_fn("[FIRST CALL] Executing source service\n")
            req = build_request(src_service, write_fn, input_fn)
            res = call_api(src_service, req, write_fn)
            if stop_flag and stop_flag.get("stop"):
                write_fn("[STOP] Execution interrupted by user.\n")
                break
            try:
                res_json = json.loads(res) if res else {}
                status = res_json.get("Status", "").lower() == "successful"
                service_result = res_json.get("Service Result", None)
            except Exception as e:
                write_fn(f"[ERROR] Parsing response for {src_service.service.name}: {e}\n")
                status = False
                service_result = None
            res_map[src_instance.id] = [status, service_result]
            output_map[src_instance.id] = service_result
            write_fn(f"[RESULT] {src_service.service.name}: Success={status}, Result={service_result}\n")

        should_execute_dst = False

        # Determine whether to execute the destination service
        if rel_type == "ordered":
            write_fn(f"[ORDERED] Executing destination service: {dst_instance.get_display_name()}\n")
            should_execute_dst = True
        elif rel_type == "on-success":
            src_result = res_map.get(src_instance.id)
            if src_result and src_result[0]:
                write_fn(f"[ON-SUCCESS] Source {src_instance.get_display_name()} successful. Executing destination: {dst_instance.get_display_name()}\n")
                should_execute_dst = True
            else:
                write_fn(f"[ON-SUCCESS] Source {src_instance.id} failed. Skipping destination: {dst_instance.id}\n")
        elif rel_type == "condition" or rel_type == "conditional":
            src_result = res_map.get(src_instance.id)
            if src_result and src_result[0] and hasattr(rel, 'condition'):
                try:
                    response_value = int(src_result[1])
                except (ValueError, TypeError):
                    response_value = src_result[1]
                condition_result = evaluate_condition(response_value, rel.condition)
                if condition_result:
                    write_fn(f"[CONDITIONAL] Condition '{rel.condition}' satisfied. Executing destination: {dst_instance.get_display_name()}\n")
                    should_execute_dst = True
                else:
                    write_fn(f"[CONDITIONAL] Condition '{rel.condition}' not satisfied. Skipping destination: {dst_instance.get_display_name()}\n")
            else:
                write_fn(f"[CONDITIONAL] Source {src_instance.get_display_name()} failed. Skipping destination: {dst_instance.get_display_name()}\n")
        else:
            write_fn(f"[WARNING] Unknown relation type: {rel.type}\n")

        if should_execute_dst:
            # Prepare the map for auto-input: if a destination input has the same name as the source output, insert it
            auto_inputs = {}
            src_output = output_map.get(src_instance.id)
            dst_input_params = getattr(dst_service.service, "input_params", {})
            if src_output is not None:
                for param in dst_input_params:
                    # If the current input value is exactly the name of the src output, replace it
                    current_val = dst_service.input_values.get(param, "")
                    if current_val == "" or current_val == str(src_output):
                        continue  # Do not replace if already set or empty
                    # If the input value is exactly the name of the src output, replace it
                    if current_val == rel.src.service.output_name:  # rel.src_output_name must be defined in the model
                        auto_inputs[param] = src_output
            req = build_request(dst_service, write_fn, input_fn, src_result_map=auto_inputs)
            res = call_api(dst_service, req, write_fn)
            if stop_flag and stop_flag.get("stop"):
                write_fn("[STOP] Execution interrupted by user.\n")
                break
            try:
                res_json = json.loads(res) if res else {}
                status = res_json.get("Status", "").lower() == "successful"
                service_result = res_json.get("Service Result", None)
            except Exception as e:
                write_fn(f"[ERROR] Parsing response for {dst_service.service.name}: {e}\n")
                status = False
                service_result = None
            res_map[dst_instance.id] = [status, service_result]
            output_map[dst_instance.id] = service_result
            write_fn(f"[RESULT] {dst_service.service.name}: Success={status}, Result={service_result}\n")

    write_fn(f"[PROMPT] EXECUTION COMPLETED\n")
    write_fn("\n[SERVICE RESULTS SUMMARY]\n")
    for k, v in res_map.items():
        service_name = service_map[k].service.name if k in service_map else k
        write_fn(f"{service_name}: Success={v[0]}, Result={v[1]}\n")