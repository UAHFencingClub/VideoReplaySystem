// Example 6 - Receiving binary data
// https://forum.arduino.cc/t/serial-input-basics-updated/382007/3
#include <HardwareSerial.h>
#include <ArduinoJson.h>

#define SG12_DEF 0x1344 //25 bytes of data

//Figure out what different timer headers mean, I think one is stopped, another is pause time and another is running, not confident
#define SG12_TIMER_TICK 0x1352 //7 
#define SG12_TIMER_UPDATE 0x1342 //TODO
#define SG12_TIMER_RESET 0x134E //9

#define SG12_LIGHTS 0x1452 //7
#define SG12_DATAMARK 0x30

const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;
HardwareSerial SerialPort(2);

StaticJsonDocument<200> sg12_data;

void setup() {
    SerialPort.begin(38400,SERIAL_8N1, 16);
    Serial.begin(115200);
    Serial.println("<Arduino is ready>");
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
      serializeJsonPretty(sg12_data, Serial);
      Serial.println();
      Serial.println();
      newData = false;
    }
}

void printHex(int num, int precision) {
  char tmp[16];
  char format[128];

  sprintf(format, " %%.%dX", precision);

  sprintf(tmp, format, num);
  Serial.print(tmp);
}

uint16_t getSG12Header() {
  uint16_t buf = (receivedBytes[0]<<8) + (receivedBytes[1]);
  return buf;
}

void recvBytesWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    byte startMarker = 0x01;
    byte endMarker = 0x04;
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

/* //For debugging, not needed otherwise
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
*/
