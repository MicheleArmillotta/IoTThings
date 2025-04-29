# Agricultural Storage Scenario - Part 1

## Description of Files and Functionality

This repository contains the scripts and executables for a project simulating a smart monitoring and control system for an **agricultural storage facility in hot climate zones**.  
The system is divided into two main components: one running on the **Raspberry Pi (edge device)** and one on the **edge server**.

---

## Raspberry Pi

This part runs directly on the Raspberry Pi and includes both **sensors** and **actuators**:

### 📡 Sensors
Located in the `sensors/` folder:  
Contains scripts and executables that interface with the **flame sensor** and the **DHT11 sensor** (temperature and humidity).

### ⚙️ Actuators
Located in the `actuators/` folder:  
Contains scripts and executables that control the **servo motor** (for the fan) and the **buzzer** (alarm system).

### 🔗 `connect.py`
This script runs on the Raspberry Pi. It:
- Initializes and activates all the sensor and actuator services.
- Sends their descriptions and live data to the edge server for remote control and monitoring.

---

## Edge Server

This part manages service registration, logic composition, and control from a centralized location:

### 📨 `accept_server.py`
- Accepts incoming service descriptions from the Raspberry Pi.
- Creates and maintains a JSON file that keeps track of all registered services.

### 🧠 `server_executer.py`
- A lightweight "IDE" that allows the user to **compose** and orchestrate services.
- Reads service definitions from the JSON file.
- Based on the user configuration in the dashboard, it controls API calls to the appropriate sensor or actuator.

### 🗂️ `services.json`
- A sample JSON file showing the registered services from the Raspberry Pi.
- Used as a reference or for testing logic compositions without actual hardware.

### 🖼️ `static/` and `templates/`
- Contain the frontend resources (HTML/CSS/JS) for the user **dashboard** interface.
- The dashboard allows users to view service data and configure automation logic.

---

Feel free to explore each folder for more detailed documentation and code comments.
