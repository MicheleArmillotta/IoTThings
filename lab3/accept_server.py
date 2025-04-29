from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Percorso del file dove salviamo i dati
services_file = "services.json"

# Funzione per caricare i servizi esistenti
def load_services():
    if os.path.exists(services_file):
        with open(services_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Funzione per salvare i servizi aggiornati
def save_services(services):
    with open(services_file, 'w') as f:
        json.dump(services, f, indent=4)

@app.route('/register', methods=['POST'])
def register_service():
    service_data = request.get_json()
    if not service_data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Aggiungiamo l'IP del client che ha fatto la richiesta
    client_ip = request.remote_addr
    service_data['client_ip'] = client_ip

    # Carichiamo i servizi esistenti
    services = load_services()

    # Aggiungiamo il nuovo servizio
    services.append(service_data)

    # Salviamo tutto
    save_services(services)

    return jsonify({"message": "Service registered successfully"}), 200

if __name__ == '__main__':
    # Il server ascolta su tutte le interfacce per ricevere anche da altri dispositivi
    app.run(host='0.0.0.0', port=5000)
