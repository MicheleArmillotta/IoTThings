import subprocess
import requests
import time
import os

# Hardcoded: Lista dei percorsi degli eseguibili dei servizi
services_paths = [
    "./actuators/buzzer_rest",  # Eseguibile C++
    "./actuators/servo_rest",
    "./sensors/dht_rest",
    "./sensors/flame_rest"
]

# Hardcoded: Informazioni da inviare all'Edge
services_info = [
    {
        "rpi_id": "raspberry-001",
        "service_name": "activate_buzzer",
        "port":18080,
        "input_number": 0,
        "input_names": []
    },
    {
        "rpi_id": "raspberry-001",
        "service_name": "activate_fan",
        "port":18081,
        "input_number": 0,
        "input_names": []
    },
    {
        "rpi_id": "raspberry-001",
        "service_name": "current_temp",
        "port":18082,
        "input_number": 0,
        "input_names": []
    },
        {
        "rpi_id": "raspberry-001",
        "service_name": "flame_status",
        "port":18083,
        "input_number": 0,
        "input_names": []
    }
]

# Hardcoded: Endpoint dell'Edge
edge_register_endpoint = "http://192.168.8.242:5000/register"
# Lista per salvare i processi avviati
processes = []

def activate_services():
    for path in services_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):  # Controlla se è eseguibile
            print(f"Starting service: {path}")
            p = subprocess.Popen([path])
            processes.append(p)
        else:
            print(f"Service {path} not found or not executable.")

def register_services():
    for service in services_info:
        try:
            response = requests.post(edge_register_endpoint, json=service)
            if response.status_code == 200:
                print(f"Successfully registered {service['service_name']}")
            else:
                print(f"Failed to register {service['service_name']} (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error registering service {service['service_name']}: {e}")

def terminate_services():
    print("\nTerminating all services...")
    for p in processes:
        try:
            p.terminate()  # Manda SIGTERM
            p.wait(timeout=5)  # Aspetta che finisca
        except Exception as e:
            print(f"Failed to terminate process: {e}")

if __name__ == "__main__":
    try:
        activate_services()
        time.sleep(2)  # Attendi un attimo che i servizi partano
        register_services()

        print("Services are active. Press Ctrl+C to stop.")

        # Aspetta indefinitamente
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        terminate_services()
        print("Exited cleanly.")
