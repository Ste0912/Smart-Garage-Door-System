#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <coap-simple.h>
#include <DHT.h>

#define DHTPIN D4
#define DHTTYPE DHT11

#define LED_PIN D1

#define OPEN_TIME 25

const char* ssid = "mannuhotspot";
const char* password = "mannuhotspot";

bool open = false;
unsigned long open_time = 0;

WiFiUDP udp;
Coap coap(udp);

DHT dht(DHTPIN, DHTTYPE);

void coap_callback(CoapPacket &packet, IPAddress ip, int port) {
  open = true;
  String response = "T: ";
  response+= dht.readTemperature();
  response+= " H:";
  response+=dht.readHumidity();
  Serial.println();
  Serial.print("[CoAp] Sending response: ");
  Serial.println(response);
  coap.sendResponse(ip, port, packet.messageid, response.c_str());
  open_time = millis();
}

void setup() {
  Serial.begin(9600);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");

  coap.server(coap_callback, "MONITOR_WEATHER");
  coap.start();
  //if coap is started successfully, it will print the IP address
  Serial.print("CoAP server started at ");
  Serial.print(WiFi.localIP());
  Serial.print(":");

  pinMode(LED_PIN, OUTPUT);
  dht.begin();
}

void loop() {
  coap.loop();
  if(open) digitalWrite(LED_PIN, HIGH);
  else digitalWrite(LED_PIN, LOW);
  if(millis() - open_time > OPEN_TIME*1000){
    open = false;
    open_time = 0;
  }
}
