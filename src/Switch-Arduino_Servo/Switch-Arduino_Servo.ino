// MIT License
// 
// Copyright (c) 2017 Axel Fischer (sweep-me.net)
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

#include <Servo.h>
Servo myservo;  // create servo object to control a servo
int oldval;


void setup() {
  // initialize serial:
  Serial.begin(9600);
  Serial.setTimeout(10);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

 // read from port 0
    if (Serial.available()) {

      //Serial.println("ok");

      digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
      int val = Serial.readString().toInt();
      //Serial.print("Value: ");
      //Serial.println(val); 
      //val = map(val, 0, 127, 0, 180);

      myservo.write(val);                  // sets the servo position according to the scaled value

      //delay(abs(oldval-val)*15);           // waits for the servo to get there
      digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW

      //int oldval = val;
  }
}
