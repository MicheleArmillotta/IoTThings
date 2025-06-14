from flask import Flask, render_template, request, jsonify
import json
import threading
import time
import requests

app = Flask(__name__)

# Load available services from JSON file
with open('services.json', 'r') as f:
    services_list = json.load(f)

# Transform the list into a dictionary: key = service_name
services = {service['service_name']: service for service in services_list}

compositions = []  # List of relationships created by the user
execution_interval = None  # Global range

print("WARNING: THIS IS TEST CODE, HARDCODED CODE, ITS NOT RELIABLE AND NOT PRODUCTION READY\n")

@app.route("/")
def index():
    return render_template("index.html", services=services)

@app.route("/save_composition", methods=["POST"])
def save_composition():
    global compositions, execution_interval
    data = request.get_json()
    compositions = data.get('compositions', [])
    execution_interval = data.get('interval', None)

    # Start the executor in a separate thread
    threading.Thread(target=executor, daemon=True).start()

    return jsonify({"status": "Composition saved and execution started"})

def executor():
    while True:
        for comp in compositions:
            service_a = comp['service_a']
            service_b = comp['service_b']
            relation = comp['relation']
            value = comp.get('expected_value', None)
            expected_value = int(value) if value is not None else None

            print(f"Executing relation: {service_a} -> {service_b} ({relation})")

            # Decides whether to call GET or POST
            method_a = "post" if "activate" in service_a.lower() else "get"
            method_b = "post" if "activate" in service_b.lower() else "get"

            #the logic of the IDE is "hardcoded", to have a general program, in which the relations can be of any type and the 
            #inputs and outputs at any scale we should change protocol and exchange more information between the services and the edge
            
            try:
                if method_a == "post":
                    resp_a = requests.post(f"http://{services[service_a]['client_ip']}:{services[service_a]['port']}/{service_a}")
                else:
                    resp_a = requests.get(f"http://{services[service_a]['client_ip']}:{services[service_a]['port']}/{service_a}")
            except Exception as e:
                print(f"Failed calling {service_a}: {e}")
                continue

            if relation == "after":
                try:
                    if method_b == "post":
                        requests.post(f"http://{services[service_b]['client_ip']}:{services[service_b]['port']}/{service_b}")
                    else:
                        requests.get(f"http://{services[service_b]['client_ip']}:{services[service_b]['port']}/{service_b}")
                except Exception as e:
                    print(f"Failed calling {service_b}: {e}")

            elif relation == "on_value":
                try:
                    if services[service_a]['service_name'] == "flame_status":
                        if resp_a.json().get('flame_detected') >= expected_value:
                            if method_b == "post":
                                requests.post(f"http://{services[service_b]['client_ip']}:{services[service_b]['port']}/{service_b}")
                            else:
                                requests.get(f"http://{services[service_b]['client_ip']}:{services[service_b]['port']}/{service_b}")
                    elif services[service_a]['service_name'] == "current_temp":
                        if resp_a.json().get('temperature') >= expected_value:
                            if method_b == "post":
                                requests.post(f"http://{services[service_b]['client_ip']}:{services[service_b]['port']}/{service_b}")
                            else:
                                requests.get(f"http://{services[service_b]['client_ip']}:{services[service_b]['port']}/{service_b}")
                except Exception as e:
                    print(f"Error parsing response from {service_a}: {e}")

        if execution_interval:
            time.sleep(execution_interval)
        else:
            break

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

