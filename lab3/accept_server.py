from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Path to the file where we save the data
services_file = "services.json"

# Function to load existing services
def load_services():
    if os.path.exists(services_file):
        with open(services_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Function to save updated services
def save_services(services):
    with open(services_file, 'w') as f:
        json.dump(services, f, indent=4)

@app.route('/register', methods=['POST'])
def register_service():
    service_data = request.get_json()
    if not service_data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Let's add the IP of the client that made the request
    client_ip = request.remote_addr
    service_data['client_ip'] = client_ip

    # Let's load existing services
    services = load_services()

    # Let's add the new service
    services.append(service_data)

    # Let's save everything
    save_services(services)

    return jsonify({"message": "Service registered successfully"}), 200

if __name__ == '__main__':
    # Il server ascolta su tutte le interfacce per ricevere anche da altri dispositivi
    app.run(host='0.0.0.0', port=5000)
