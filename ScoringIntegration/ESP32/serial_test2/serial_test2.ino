// Example 6 - Receiving binary data
// https://forum.arduino.cc/t/serial-input-basics-updated/382007/3
#include <HardwareSerial.h>
const byte numBytes = 32;
byte receivedBytes[numBytes];
byte numReceived = 0;

boolean newData = false;
HardwareSerial SerialPort(2);

void setup() {
  SerialPort.begin(38400,SERIAL_8N1, 16);
    Serial.begin(115200);
    Serial.println("<Arduino is ready>");
}

void loop() {
    recvBytesWithStartEndMarkers();
    int header = getSG12Header();
    //printHex(header,4);
    //Serial.println();
    showNewData();
}

void printHex(int num, int precision) {
  char tmp[16];
  char format[128];

  sprintf(format, " %%.%dX", precision);

  sprintf(tmp, format, num);
  Serial.print(tmp);
}

uint16_t getSG12Header() {
  return receivedBytes[0]<<8 + receivedBytes[1];
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
