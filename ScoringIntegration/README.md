# SG12 Scoring Integration

This script for the ESP32 is for interfacing the SG12 Fencing Scoring machine with some web UI.

It uses a max485 based board to convert the logic levels from the RS-422 port on the box to convert the logic levels needed to then connect to the UART (Serial) interfaces of the ESP32. 

The ESP32 then sends http post requests to a webserver. It was originally desired to use websockets, but the server that was made used SocketIO which was slightly different.

## Protocol

Packets sent begin with 0x01 and end with 0x04. Some of the packet headers we have identified are the following:
- SG12_DEF: 0x1344 (25 bytes long) Contains the left and right scores and cards (Can't seem to get the right red card)
- SG12_TIMER_TICK: 0x1352 (7 bytes long)  Contains the timer time and maybe some other stuff too.
- SG12_TIMER_UPDATE: 0x1342 (? bytes long) Contains the timer time and maybe some other stuff too.
- SG12_TIMER_RESET: 0x134E (9 bytes long) Contains the timer time and maybe some other stuff too.
- SG12_LIGHTS: 0x1452 (7 bytes long) Contains data about what lights are on (left/right touch/offtarget) may include grounding?

These names may not be as descriptive or quite representitive of the data (more specifically the SG12_TIMER_TICK and SG12_TIMER_UPDATE).

Data seems to exists as the lower nibble of data of a byte with an upper nibble of 0x3. 

## TODO
- [ ] Not sure where the data for the right redcard is located (may just be broken on our machine). 
- [ ] Grounding Lights were not a consideration at the time.
- [ ] Timer headers may contain some extra info that we don't know.
- [ ] Method of sending the HTTP server IP over serial.
- [ ] Method of sending WiFi info over serial.
- [ ] Status light.

## Pictures
TODO
