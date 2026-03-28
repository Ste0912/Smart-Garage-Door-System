# IoT Identity & Access Management (IAM) Architecture: Smart Garage System
An end-to-end Identity & Access Management (IAM) architecture designed specifically for IoT environments. This project provides a secure, role-based framework for managing physical access in residential or corporate contexts, prioritizing unauthorized access prevention, cryptographic security, and comprehensive environmental/audit monitoring.


## Security Architecture & IAM
The system is built on a distributed, zero-trust inspired architecture, securing the perimeter from the edge IoT nodes to the centralized API backend:
**Edge Authentication & Access Control:** ESP8266 edge nodes manage physical entry and exit points utilizing MFRC522 RFID readers over lightweight, machine-to-machine protocols (MQTT/CoAP).
**Real-Time Validation & Message Brokerage:** An asynchronous MQTT handler processes RFID scan payloads in real-time, validating credentials against a secure MongoDB database to dynamically update access status and mitigate replay attacks.
**API Security & Temporary Tokens:** A Flask-based RESTful API backend handles telemetry and administrative requests. Endpoints are heavily secured utilizing short-lived temporary token (`temp_token`) validation and strict firewall logic to prevent unauthorized external access.
**Cryptographic Hashing:** User credentials and sensitive authentication materials are protected using **Argon2** cryptographic hashing, ensuring high resistance against brute-force and dictionary attacks.
**Secure Telemetry & Audit Trails:** A robust Telegram bot interface acts as the administrative client, providing secure CLI-like access to system logs, usage statistics, and real-time audit trails.

## Core Security Features

* **Strict Role-Based Access Control (RBAC):** Implementation of deep RBAC logic to enforce the principle of least privilege. The system rigidly distinguishes between standard users and administrators.
**Privilege Escalation Prevention:** Sensitive administrative functions (e.g., registering or deleting access entities) require explicit administrative privileges and secondary password verification, effectively mitigating vertical privilege escalation attempts by non-privileged users.
**Continuous Audit & Monitoring:** Reliable tracking of all access events (timestamps, UID matching) and aggregated historical telemetry, providing administrators with transparent visibility into potential security anomalies.
* **Schema Validation & Data Integrity:** MongoDB collections are strictly enforced using YAML schemas, guaranteeing data integrity and preventing NoSQL injection or malformed data payload attacks.

## Tech Stack & Security Tools

* **Hardware:** ESP8266 Microcontrollers, MFRC522 RFID Readers, I2C LCD Displays, DHT11 Sensor.
* **Protocols:** MQTT, CoAP, HTTP/REST.
* **Backend Framework:** Python 3.10, Flask, python-telegram-bot, Paho-MQTT.
* **Security Mechanisms:** Argon2 Hashing, Token-based Authentication, RBAC, Schema Validation.
* **Data & Infrastructure:** MongoDB (Strict YAML Schemas), Eclipse Mosquitto (MQTT Broker), ngrok (Webhook exposure).

## Installation & Setup
## Prerequisites

Ensure you have the following installed and configured on your host machine:
* Python 3.10
* MongoDB
* Eclipse Mosquitto

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Ste0912/SMART_GARAGE_DOOR.git](https://github.com/Ste0912/SMART_GARAGE_DOOR.git)
   cd SMART_GARAGE_DOOR

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Ste0912/SMART_GARAGE_DOOR.git](https://githu/SMART_GARAGE_DOOR.git)
   cd SMART_GARAGE_DOOR
   ```

2. **Start the required background services:**
   
   Ensure MongoDB and your MQTT broker are running.
   ```bash
    net start mongodb
    mosquitto -v -c "path\to\your\mosquitto.conf"
   ```
3. **Set up the Python environment:**
   
   Create and activate a virtual environment, then install dependencies.
   ```bash
   python3.10 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   
   ```bash
   python app.py
   ```

## Available Bot Commands

The Telegram interface supports a wide array of commands to manage the system:

* **General:** `/start`, `/help`, `/login <user> <pwd>`, `/logout`
* **Statistics:** `/get_open_times`, `/get_total_open_times`, `/get_open_times_stats`
* **Management (Admin Only):** `/register_pedestrian`, `/delete_pedestrian`, `/find_pedestrian`, `/register_car`, `/delete_car`, `/find_car`

