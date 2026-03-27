# Smart-Garage-Door-System

An end-to-end IoT solution for managing secure garage access and environmental monitoring. This system integrates edge hardware authentication with a centralized Python backend, leveraging a Telegram bot interface for remote administration and comprehensive statistical tracking.

## System Architecture

The project is built on a distributed, secure architecture utilizing lightweight machine-to-machine communication protocols and a robust API backend:
* **Access Control & IoT Edge:** ESP8266 edge nodes manage entry and exit using MFRC522 RFID readers. 
* **Message Brokerage:** An MQTT handler runs asynchronously to process incoming RFID scans in real-time. It queries a MongoDB database to match UIDs, logs the entry/exit timestamps, and dynamically updates the user's `atHome` status.
* **RESTful API Backend:** A Flask-based server processes incoming telemetry and administrative actions. API endpoints for user and car management are secured using temporary token validation (`temp_token`) to prevent unauthorized access.
* **Telegram Interface:** A robust CLI-like Telegram bot allows users to authenticate and interact with the system.

## Core Features

* **Role-Based Access Control (RBAC):** The system distinguishes between standard users and administrators. Sensitive operations, such as registering or deleting cars and pedestrians, require administrative privileges and a verified admin password.
* **Comprehensive Telemetry & Statistics:** Administrators and authenticated users can retrieve detailed usage statistics, including total open times and aggregated historical data (e.g., daily, weekly, or monthly usage).
* **Structured Data Management:** MongoDB collections are strictly structured using YAML schemas, ensuring consistent data types for user profiles, credentials, and access logs. 
* **Remote Administration:** Administrators can manage the entire database directly through the Telegram bot using commands like `/register_car`, `/delete_pedestrian`, and `/find_car`.

## Tech Stack

* **Hardware:** ESP8266 Microcontrollers, MFRC522 RFID Readers, I2C LCD Displays, DHT11 Sensor.
* **Protocols:** MQTT, CoAP, HTTP/REST.
* **Backend:** Python 3.10, Flask, python-telegram-bot, Paho-MQTT.
* **Database:** MongoDB (with strict YAML schema validation).
* **Infrastructure:** Mosquitto (MQTT Broker), ngrok (Webhook exposure).

## Available Bot Commands

The Telegram interface supports a wide array of commands to manage the system:

* **General:** `/start`, `/help`, `/login <user> <pwd>`, `/logout`
* **Statistics:** `/get_open_times`, `/get_total_open_times`, `/get_open_times_stats`
* **Management (Admin Only):** `/register_pedestrian`, `/delete_pedestrian`, `/find_pedestrian`, `/register_car`, `/delete_car`, `/find_car`

## Prerequisites

Ensure you have the following installed and configured on your host machine:
* Python 3.10
* MongoDB
* Eclipse Mosquitto

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Ste0912/SMART_GARAGE_DOOR.git](https://githu/SMART_GARAGE_DOOR.git)
   cd SMART_GARAGE_DOOR
   ```
 * Start the required background services:
   Ensure MongoDB and your MQTT broker are running.
   ```bash
    net start mongodb
    mosquitto -v -c "path\to\your\mosquitto.conf"
   ```
 * Set up the Python environment:
   Create and activate a virtual environment, then install dependencies.
   ```bash
   python3.10 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
 * Run the Application:
   ```bash
   python app.py
   ```

