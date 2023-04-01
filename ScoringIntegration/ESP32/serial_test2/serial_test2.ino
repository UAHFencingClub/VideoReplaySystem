// Some code pulled from https://forum.arduino.cc/t/serial-input-basics-updated/382007/3

//#define DEBUG

#include <HardwareSerial.h>
#include <ArduinoJson.h>
#include "WiFi.h"
#include <HTTPClient.h>

//SG12 info
#define SG12_DEF 0x1344 //25 bytes of data

//Figure out what different timer headers mean, I think one is stopped, another is pause time and another is running, not confident
#define SG12_TIMER_TICK 0x1352 //7 
#define SG12_TIMER_UPDATE 0x1342 //TODO
#define SG12_TIMER_RESET 0x134E //9

#define SG12_LIGHTS 0x1452 //7
#define SG12_DATAMARK 0x30

#define SG12_START 0x01
#define SG12_END   0x04

//Serial Data related variables
const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;
HardwareSerial SerialPort(2);

StaticJsonDocument<200> sg12_data;

//Wifi related variables
const char* ssid = "Student5";
const char* password = "Go Chargers!";

int btnGPIO = 0;
int btnState = false;

WiFiClient client;

#define HTTP_SERVER_IP String("10.4.145.139:5000")

void setup() {
    SerialPort.begin(38400,SERIAL_8N1, 16);
    Serial.begin(115200);
    Serial.println("<Arduino is ready>");

    connectToWiFi();
}

void loop() {

    recvBytesWithStartEndMarkers();
    int header = getSG12Header();
    if (newData) {
      switch (header) {
        case SG12_DEF: {
          uint8_t right_ones_score = receivedBytes[4] - SG12_DATAMARK;
          uint8_t right_tens_score = receivedBytes[3] - SG12_DATAMARK;
          sg12_data["right_score"] = 10*right_tens_score + right_ones_score;
    
          
          uint8_t left_ones_score = receivedBytes[7] - SG12_DATAMARK;
          uint8_t left_tens_score = receivedBytes[6] - SG12_DATAMARK;
          sg12_data["left_score"] = 10*left_tens_score + left_ones_score;
    
          sg12_data["left_yellow"] = receivedBytes[16] - SG12_DATAMARK;
          sg12_data["left_red"] = receivedBytes[18] - SG12_DATAMARK;
    
          sg12_data["right_yellow"] = receivedBytes[10] - SG12_DATAMARK;
          sg12_data["right_red"] = 0; //Unknown data location, further investigation needed
          break;
        }
        case SG12_TIMER_TICK:
        case SG12_TIMER_RESET:
        case SG12_TIMER_UPDATE: {
          uint8_t time_min = receivedBytes[4] - SG12_DATAMARK; 
          uint8_t time_tens = receivedBytes[6] - SG12_DATAMARK; 
          uint8_t time_ones = receivedBytes[7] - SG12_DATAMARK;
          sg12_data["time"] = 60*time_min + (10*time_tens + time_ones);
          break;
        }
        case SG12_LIGHTS: {
          sg12_data["left_touch"] = receivedBytes[2] - SG12_DATAMARK;
          sg12_data["right_touch"]  = receivedBytes[4] - SG12_DATAMARK;
    
          sg12_data["left_offtarget"] = receivedBytes[8] - SG12_DATAMARK;
          sg12_data["right_offtarget"] = receivedBytes[6] - SG12_DATAMARK;
          break;
        }
      }
      //serializeJsonPretty(sg12_data, Serial);
      //Serial.println();
      //Serial.println();

      HTTPClient http;

      String serialized_sg12_data;
      serializeJson(sg12_data, serialized_sg12_data);

      http.begin("http://"+HTTP_SERVER_IP+"/api/score");               //Specify destination for HTTP request
      http.addHeader("Content-Type", "application/json");             //Specify content-type header
  
      int httpResponseCode = http.POST(serialized_sg12_data);


      #ifdef DEBUG
      Serial.print("HTTP Response: ");
      Serial.println(httpResponseCode,DEC);

      serializeJsonPretty(sg12_data,Serial);

      Serial.println();
      Serial.println();

      showNewData();  

      Serial.println("#######################################");
      #endif
      
      newData = false;
    }
}

uint16_t getSG12Header() {
  uint16_t buf = (receivedBytes[0]<<8) + (receivedBytes[1]);
  return buf;
}

void connectToWiFi() {
  pinMode(btnGPIO, INPUT);
  Serial.println();
  Serial.print("[WiFi-test] Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  int tryDelay = 500;
  int numberOfTries = 20;
  bool is_not_connected = true;
  while (is_not_connected) {
        switch(WiFi.status()) {
          case WL_NO_SSID_AVAIL:
            Serial.println("[WiFi] SSID not found");
            break;
          case WL_CONNECT_FAILED:
            Serial.print("[WiFi] Failed - WiFi not connected! Reason: ");
            return;
            break;
          case WL_CONNECTION_LOST:
            Serial.println("[WiFi] Connection was lost");
            break;
          case WL_SCAN_COMPLETED:
            Serial.println("[WiFi] Scan is completed");
            break;
          case WL_DISCONNECTED:
            Serial.println("[WiFi] WiFi is disconnected");
            break;
          case WL_CONNECTED:
            Serial.println("[WiFi] WiFi is connected!");
            Serial.print("[WiFi] IP address: ");
            Serial.println(WiFi.localIP());
            is_not_connected = false;
            break;
          default:
            Serial.print("[WiFi] WiFi Status: ");
            Serial.println(WiFi.status());
            break;
        }
        delay(tryDelay);
        
        if(numberOfTries <= 0){
          Serial.print("[WiFi] Failed to connect to WiFi!");
          // Use disconnect function to force stop trying to connect
          WiFi.disconnect();
          return;
        } else {
          numberOfTries--;
        }
  }
  delay(1000); 
}

void recvBytesWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    byte startMarker = SG12_START;
    byte endMarker = SG12_END;
    byte rb;
   

    while (SerialPort.available() > 0 && newData == false) {
        rb = SerialPort.read();

        if (recvInProgress == true) {
            if (rb != endMarker) {
                receivedBytes[ndx] = rb;
                ndx++;
                if (ndx >= numBytes) {
                    ndx = numBytes - 1;
                }
            }
            else {
                receivedBytes[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                numReceived = ndx;  // save the number for use when printing
                ndx = 0;
                newData = true;
            }
        }

        else if (rb == startMarker) {
            recvInProgress = true;
        }
    }
}

#ifdef DEBUG
void printHex(int num, int precision) {
  char tmp[16];
  char format[128];

  sprintf(format, " %%.%dX", precision);

  sprintf(tmp, format, num);
  Serial.print(tmp);
}

void showNewData() {
    if (newData == true) {
        Serial.print("This just in (HEX values)... ");
        for (byte n = 0; n < numReceived; n++) {
            Serial.print(receivedBytes[n], HEX);
            Serial.print(' ');
        }
        Serial.println();
        newData = false;
    }
}
#endif
