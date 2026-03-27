#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <coap-simple.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_PCF8574.h>
#include <ArduinoJson.h>
#include <string.h>

#define WIFI_SSID "mannuhotspot"
#define WIFI_PASS "mannuhotspot"

#define MQTT_SERVER "192.168.158.172"
#define MQTT_PORT 1883
#define MQTT_TOPIC "smart_garage_door/exit"
#define MQTT_CODE "\"EXIT"
#define MQTT_ERROR "\"ERROR"
#define MQTT_CLIENT "exit_node"
#define Coap1 192
#define Coap2 168
#define Coap3 158
#define Coap4 67

#define COAP_RESOURCE "MONITOR_WEATHER"

#define SS_PIN D2
#define RST_PIN D1

#define I2C_LCD_ADDR 0x27

#define CLEAR_TIME 5

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_PCF8574 lcd(I2C_LCD_ADDR);

//MQTT
WiFiClient espClient;
PubSubClient client(espClient);

//COAP
WiFiUDP udp;
Coap coap(udp);
IPAddress serverIP(Coap1, Coap2,Coap3, Coap4);
const int serverPort = 5683;
unsigned long open_time = 0;

void showOnLCD(String line1, String line2 = "") {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

void setup_wifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");

  Serial.print("Connected to IP ");
  Serial.println(WiFi.localIP());
}

void reconnect(){
  while (!client.connected()) {
    Serial.print("MQTT, connecting to ");
    Serial.print((char*)MQTT_SERVER);
    Serial.println("... ");
    if (client.connect((char*)MQTT_CLIENT)) {
      client.subscribe((char*)MQTT_TOPIC);
      Serial.print("MQTT connected to ");
      Serial.println((char*)MQTT_TOPIC);
    } else {
      Serial.println();
      Serial.print("MQTT fail, rc=");
      Serial.println(String(client.state()));
      delay(5000);
    }
  }
}

// COAP: Handle responses from server
void CoAp_callback(CoapPacket &packet, IPAddress ip, int port) {
  Serial.print("[CoAP]: Response: ");
  String payload = "";
  for (int i = 0; i < packet.payloadlen; i++) payload += (char)packet.payload[i];
  Serial.println(payload);
  lcd.setCursor(0, 1);
  lcd.print(payload);
}

//MQTT
void MQTT_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  for (int i = 0; i < length; i++) {
      Serial.print((char)payload[i]);
  }
  Serial.println();

  bool authorised = false;
  String line1 = "";

  if(strcmp(topic, (char*)MQTT_TOPIC) == 0){
    if (strncmp((char*)payload, (char*)MQTT_CODE, sizeof(MQTT_CODE)-1) == 0) {
      line1="Bye  ";
      for (int i = sizeof(MQTT_CODE); i < length-1; i++) line1+=(char)payload[i];
      Serial.println(line1);
      showOnLCD(line1);
      authorised = true;
      open_time = millis();
    } else if (strncmp((char*)payload, (char*)MQTT_ERROR, sizeof(MQTT_ERROR)-1) == 0) {
      for (int i = sizeof(MQTT_ERROR); i < length-1; i++) line1+=(char)payload[i];
      Serial.println(line1);
      showOnLCD(line1);
      authorised = false;
      open_time = millis();
    }
  }

  if(authorised){
    Serial.println("[CoAP] Sending GET /MONITOR WEATHER");
    coap.get(serverIP, serverPort, (char*)COAP_RESOURCE);
    Serial.println("[CoAP] GET /MONITOR WEATHER sent");
  }
}

void reconnectWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.print("Wifi");
      WiFi.begin(WIFI_SSID, WIFI_PASS);
      while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
      }
      Serial.println("Wifi connected");
    }
}

void publishUID(String uid_string){
  if (!client.connected())
    while (!client.connected()) client.connect((char*)MQTT_CLIENT);
  client.loop();

  StaticJsonDocument<128> doc;
  doc["uid"] = uid_string;
  char buffer[128];
  serializeJson(doc, buffer);

  client.publish((char*)MQTT_TOPIC, buffer);
}

String RFIDRead(){
  String readUid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    readUid += String(rfid.uid.uidByte[i]) + " ";
  }
  readUid.trim();
  return readUid;
}

void setup() {
  Serial.begin(9600);
  setup_wifi();
  client.setServer(MQTT_SERVER, 1883);
  client.setCallback(MQTT_callback);
  
  SPI.begin();
  rfid.PCD_Init();

  //Setup CoAP response callback
  coap.response(CoAp_callback);
  coap.start();

  Wire.begin(0, 2);
  lcd.begin(16,2);
  lcd.setBacklight(255);
  showOnLCD("Ready");
}

void loop() {
  if(millis() - open_time > CLEAR_TIME*1000){
    lcd.clear();
    open_time = 0;
  }

  if (!client.connected()) reconnect();
  client.loop();
  reconnectWiFi();
  coap.loop();

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  String uid = RFIDRead();  
  publishUID(uid);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}