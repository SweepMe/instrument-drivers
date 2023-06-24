// MIT License
// 
// Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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

unsigned char sensorPin = 2; // Sensor Input
unsigned long now;
unsigned long last = 0;
unsigned long count = 0;
unsigned long duration_us = 0 ; // time between two pulses
unsigned long timer0_overflow_count;
String command;

void pulse () // Interrupt function
{
   now = micros();
   duration_us = now-last;
   last = now;
   count++;
}

void setup()
{
   pinMode(sensorPin, INPUT_PULLUP);
   Serial.begin(57600);
   attachInterrupt(digitalPinToInterrupt(sensorPin), pulse, FALLING); // Setup Interrupt
   Serial.println("Arduino initialized");
}

void loop ()
{    
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    Serial.print(count);
    Serial.print(",");
    Serial.println(duration_us, DEC);
  }
}
