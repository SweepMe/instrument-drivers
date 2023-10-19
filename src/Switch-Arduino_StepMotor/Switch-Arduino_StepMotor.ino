// MIT License
// 
// Copyright (c) 2017-2019 Axel Fischer (sweep-me.net)
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.


#include <Stepper.h>
// Declare the used pins
int dirA = 2;
int dirB = 8;
int pwmA = 3;
int pwmB = 9;

// Declare a Stepper motor with 200 steps 
Stepper stepper100(100, dirA, dirB);
Stepper stepper200(200, dirA, dirB);
Stepper stepper2048(2048, 8, 10, 9 ,11);

int speed = 10;
int type = 200;

const int ledPin = 13; // Port, an den die LED angeschlossen ist
String cmd; // String for storing serial input


void setup() {

  {
  // start serial communication to see whats happening beside your motor
  Serial.begin(9600);
  Serial.setTimeout(1000);
  }

  pinMode(ledPin, OUTPUT);

  
  // PWM pins require declaration when used as Digital
  pinMode(pwmA, OUTPUT);
  pinMode(pwmB, OUTPUT);
  
  // Set PWM pins as always HIGH
  digitalWrite(pwmA, HIGH);
  digitalWrite(pwmB, LOW);  


  stepper100.setSpeed(speed);
  stepper200.setSpeed(speed);
  stepper2048.setSpeed(speed);

  Serial.println("Ready to use");
}

void loop(){

   if (Serial.available() > 0) 
  {
    cmd = Serial.readStringUntil('\n');

    if (cmd != "")
        {

          cmd.replace(" ", "");
          Serial.println(cmd);


          // All commands ending with ? will ask for a certain parameter
          if (cmd.indexOf('?') > 0)

            {
            int index;
            String key;
            
            index = cmd.indexOf('?');
            key = cmd.substring(0,index);

            if (key == "Speed")
              {
                Serial.println(speed);
              }
            else if (key == "Type")
              {
                Serial.println(type);
              }
            }

          // All commands ending with = will set a certain parameter
          if (cmd.indexOf('=') > 0)

            {
            int index;
            String key;
            int value;
            
            index = cmd.indexOf('=');
            key = cmd.substring(0,index);
            value = cmd.substring(index+1).toInt();

            Serial.println(value);

            if (key == "Speed")
            {
                if (type == 100)
                  {
                    stepper100.setSpeed(value);
                  }
                else if (type == 200)
                  {
                    stepper200.setSpeed(value);
                  }
                else if (type == 2048)
                  {
                    stepper2048.setSpeed(value);
                  }
                
                speed = value;
            }

            if (key == "Type")
            {
                type = value;
            }
            
            else if (key == "Step")
            {
                // Set PWM pins to move
                digitalWrite(pwmA, HIGH);
                digitalWrite(pwmB, HIGH);  

                // go some steps

                if (type == 100)
                  {
                    stepper100.step(value);
                  }
                else if (type == 200)
                  {
                    stepper200.step(value);
                  }
                else if (type == 2048)
                  {
                    stepper2048.step(value);
                  }
                  
                Serial.println("reached"); // inform the user when the position has reached to go on with the next steps...
                
                // Set PWM pins to pause position
                digitalWrite(pwmA, HIGH);
                digitalWrite(pwmB, LOW);  
            }

            else
            {
              Serial.println("Command unknown"); // inform the user that no case was detected
            }
  
 
              
            }
          

        }
      

  }

}
