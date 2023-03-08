
int voltage_in_pin = 44; //using GPIO 44 for input
int value =0;

void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);

//pinMode(voltage_in_pin,INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  value = analogRead(voltage_in_pin);
Serial.println(value);
delay(500);
  //if (voltage_in_pin != 17){
  //  Serial.println("not here by this");
  //}
  //else{
  // Serial.println("all good");
  //}
}
