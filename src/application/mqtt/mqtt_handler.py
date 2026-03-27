import json, logging, time, os
import paho.mqtt.client as mqtt
from flask import current_app
from datetime import datetime
from threading import Thread, Event
from .mqtt_elaborate import elaborate_mqtt
from config.utils import getenv_array

class MQTTHandler:
    def __init__(self, app):
        self.app = app
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self._setup_mqtt()
        self.connected = False
        self.stopping = Event()
        self.reconnect_thread = None

    def _setup_mqtt(self):
        """Setup MQTT client using environment variables"""
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.username = os.getenv("MQTT_USERNAME", "")
        self.password = os.getenv("MQTT_PASSWORD", "")
        self.base_topic = os.getenv("DB_NAME")
        self.topics_list = getenv_array("TOPICS_LIST")

        if self.username.strip():
            self.client.username_pw_set(self.username, self.password)

    def start(self):
        """Start MQTT client in non-blocking way"""
        try:
            self.client.loop_start()
            self._connect()
            self.reconnect_thread = Thread(target=self._reconnection_loop)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()
            print("MQTT handler started")
        except Exception as e:
            print(f"Error starting MQTT handler: {e}")

    def stop(self):
        """Stop MQTT client"""
        self.stopping.set()
        if self.reconnect_thread:
            self.reconnect_thread.join(timeout=1.0)
        self.client.loop_stop()
        if self.connected:
            self.client.disconnect()
        print("MQTT handler stopped")

    def _connect(self):
        """Attempt to connect to the broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            print(f"Attempting connection to {self.broker}:{self.port}")
        except Exception as e:
            print(f"Connection attempt failed: {e}")
            self.connected = False

    def _reconnection_loop(self):
        """Background thread that handles reconnection"""
        while not self.stopping.is_set():
            if not self.connected:
                print("Attempting to reconnect...")
                try:
                    self._connect()
                except Exception as e:
                    print(f"Reconnection attempt failed: {e}")
            time.sleep(5)

    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection to broker"""
        if rc == 0:
            self.connected = True
            print(f"Connected to MQTT broker {self.broker}:{self.port}")
            # Subscribe to topics
            for topic in self.topics_list:
                topic = topic.strip()
                if topic:
                    self.client.subscribe(self.base_topic + "/" + topic)
                    print(f"Subscribed to topic: {self.base_topic + '/' + topic}")
        else:
            self.connected = False
            print(f"Failed to connect to MQTT broker with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection from broker"""
        self.connected = False
        if rc != 0:
            print(f"Unexpected disconnection from MQTT broker: {rc}")

    def _on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        print(f"[MQTT] message received on {msg.topic}: {msg.payload.decode()}")
        do_next = elaborate_mqtt(msg)
        if do_next["action"] == "Nothing":
            pass
        elif do_next["action"]== "MQTT and CLEAR":
            self.publish(do_next["params"]["topic"], do_next["params"]["payload"])

    def publish(self, topic, payload):
        """Publish"""
        if not self.connected:
            print("Not connected to MQTT broker")
            return

        try:
            self.client.publish(topic, json.dumps(payload), retain=False)
            print(f"Published message to {topic}: {payload}")
        except Exception as e:
            print(f"Error publishing: {e}")

    @property
    def is_connected(self):
        """Check if client is currently connected"""
        return self.connected