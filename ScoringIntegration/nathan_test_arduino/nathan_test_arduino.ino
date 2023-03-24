void setup() {
  Serial.begin(115200);
Serial1.begin(38400);
}

void printHex(int num, int precision) {
      char tmp[16];
      char format[128];

      sprintf(format, " %%.%dX", precision);

      sprintf(tmp, format, num);
      Serial.print(tmp);
}

bool active = true;
int buffer_place = 0;
byte buf[4];
int my_place = 0;
int value[100];
int l_ones_score = 0;
int l_tens_score = 0;
int r_ones_score = 0;
int r_tens_score = 0;
int l_yellow = 0;
int l_red = 0;
int r_yellow = 0;
int time_min = 0;
int time_tens = 0;
int time_ones = 0;
void loop() {

  while(Serial1.available()){
    buf[buffer_place] = Serial1.read();
    value[my_place] = buf[buffer_place];
    my_place++;
    buffer_place = (buffer_place +1)%4;
    active = true;
  }
  {
    int i = buffer_place;
    if ( active && ( (buf[i]==0x30) && (buf[(i+1)%4]==0x77) && (buf[(i+2)%4]==0x30)&& (buf[(i+3)%4]==0x4) ) ){
      //Serial.println("hello");
      for(int a=0; a<my_place; a++){
    printHex(value[a],2);
      }
      Serial.println("thats all folks");
      if( (value[0]==0x01) && (value[1]==0x13) && (value[2]==0x44)){
        // right/left score, left yellow/red card, & right yellow card
        r_ones_score = value[5] - 0x30;
        r_tens_score = value[4] - 0x30;
        Serial.print("The right score is ");
        Serial.print(r_tens_score);
        Serial.println(r_ones_score);
        
        l_ones_score = value[8] - 0x30;
        l_tens_score = value[7] - 0x30;
        Serial.print("The left score is ");
        Serial.print(l_tens_score);
        Serial.println(l_ones_score);

        l_yellow = value[17] - 0x30;
        l_red = value[19] - 0x30;
        if (l_yellow == 1){
          Serial.println("Left Yellow Card!");
        }
        else if(l_red == 1){
          Serial.println("Left Red Card!");
        }
        else{
          Serial.println("Left No Card");
        }
        r_yellow = value[11] - 0x30;
        if (r_yellow == 1){
          Serial.print("Right Yellow Card!");
        }
        else{
          Serial.print("Right No Card");
        }
        
      }
     else if( (value[0]==0x01) && (value[1]==0x13) && (value[2]==0x52)){
      // time countdown
       time_min = value[47] - 0x30; 
       time_tens = value[49] - 0x30; 
       time_ones = value[50] - 0x30;
       Serial.println();
       Serial.print("The time is ");
       Serial.print(time_min);
       Serial.print(":");
       Serial.print(time_tens);
       Serial.println(time_ones);
      }
      else if( (value[0]==0x01) && (value[1]==0x13) && (value[2]==0x42)){
        // time is paused & increment/decrement time
      }
      else if( (value[0]==0x01) && (value[1]==0x13) && (value[2]==0x4E)){
        // time reset indicator
       time_min = 3; //value[47] - 0x30; 
       time_tens = 0; //value[49] - 0x30; 
       time_ones = 0; //value[50] - 0x30;
       Serial.println();
       Serial.print("The time is ");
       Serial.print(time_min);
       Serial.print(":");
       Serial.print(time_tens);
       Serial.println(time_ones);
      }
      else if( (value[0]==0x01) && (value[1]==0x14) && (value[2]==0x52)){
        // lights
      }
    my_place=0;
      active = false;
      
    }

}
}
