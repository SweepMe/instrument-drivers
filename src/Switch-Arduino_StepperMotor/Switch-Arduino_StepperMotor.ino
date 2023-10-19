// GPL v3 License
//
//Arduino code to control a motor stepper via COM port
//Copyright (C) 2023  SweepMe! GmbH (sweep-me.net)
//
//This program is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//This program is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with this program.  If not, see <https://www.gnu.org/licenses/>.

// must be installed with Library manager
#include <AccelStepper.h>  // tested with version AccelStepper 1.6.4

// for writing/reading EEPROM to save/load positions
#include <EEPROM.h>

String command;

String idn_string = "SweepMe! GmbH,Arduino Stepper controller,1.0.0";

// motor driver type
int motor_driver_type = 1;

// motor pins 
int motor_pin1 = 6;
int motor_pin2 = 7;
int motor_pin3 = 8;
int motor_pin4 = 9;

// only pin 2 and 3 allow for interrupts at most Arduinos
int limit_switch_pin_lower = 2;
int limit_switch_pin_upper = 3;
int limit_switch_config = 3;
bool activate_lower_switch = true;
bool activate_upper_switch = true;

volatile int limit_switch_state;
volatile int limit_switch_state_lower;
volatile int limit_switch_state_upper;

int homing_speed = 1000;
int max_homing_steps = 1000;

// Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5
AccelStepper stepper(motor_driver_type, motor_pin1, motor_pin2); 


void update_limit_switch_states()
{
  if (activate_lower_switch) {
    limit_switch_state_lower = digitalRead(limit_switch_pin_lower);
  }
  if (activate_upper_switch) {
    limit_switch_state_upper = digitalRead(limit_switch_pin_upper);
  }
  

  if (limit_switch_state_lower == 1 || limit_switch_state_upper == 1)
  {
    stepper.stop();
    stepper.setSpeed(0);
    stepper.runSpeed();
    stepper.moveTo(stepper.currentPosition());  // makes sure there is zero distance to go
    limit_switch_state = true;
    digitalWrite(13, HIGH);
  }
  else
  {
    limit_switch_state = false;
    digitalWrite(13, LOW);
  }
}


void on_home()
{

  int max_homing_steps = 1000;
  
  stepper.setSpeed(-homing_speed);
  
  // waiting to reach the limit switch
  while (true)
    {
      limit_switch_state_lower = digitalRead(limit_switch_pin_lower);
      if (limit_switch_state_lower == 0){
      stepper.runSpeed();
      }
      else {
        break;
      }
    }

  // the motor automatically stops because of interrupts

  while (true) {

    limit_switch_state_lower = digitalRead(limit_switch_pin_lower);
    if (limit_switch_state_lower == 0){
      stepper.setCurrentPosition(0);
      break;
    }  

    // relative move out of the limit switch
    // move() does sometimes not work so moveTo() is used
    stepper.moveTo(stepper.targetPosition() + 1);  
    stepper.runToPosition();  // trigger the move
    max_homing_steps -= 1;
    if (max_homing_steps == 0){
      Serial.println("Homing failed");
      break;
    } 
  }
}



void setup()
{
  stepper.setMaxSpeed(1000);

  stepper.setAcceleration(1000);
  //stepper.setEnablePin(8);
  stepper.setMinPulseWidth(100);

  update_limit_switch_states();

  pinMode(13, OUTPUT);    // sets the LED pin to output mode
  attachInterrupt(digitalPinToInterrupt(limit_switch_pin_lower), update_limit_switch_states, CHANGE);
  attachInterrupt(digitalPinToInterrupt(limit_switch_pin_upper), update_limit_switch_states, CHANGE);

  Serial.begin(57600);  // set Arduino to baudrate 57600
  Serial.setTimeout(1000); // change timeout if necessary, default is 1000 ms
  Serial.println("Arduino stepper motor initialized"); // send some text to let SweepMe! know that the Arduino has finished the setup() function
}


void loop()
{
  if (limit_switch_state == false)
    {
    stepper.run();  // no limit switch
    }
  else if (limit_switch_state_lower && (stepper.distanceToGo()>0))
    {
    stepper.run();  // lower limit switch activated, only positive moves
    }
  else if (limit_switch_state_upper && (stepper.distanceToGo()<0))
    {
    stepper.run();  // upper limit switch activated, only negative moves
    }
  
  if (Serial.available()) {
       
    command = Serial.readStringUntil('\n'); // make sure you have '\n', "\n" does not work

    command.toUpperCase();  // commands are not case-sensitive
    command.replace(" ", "");  // removes all white spaces


    if (command == "R?") {
        bool running = stepper.isRunning();
        Serial.println(running);
       }
	   
    else if (command == "IDN?") {
        Serial.println(idn_string);
       }
	   
    else if (command == "P?") {
        long pos = stepper.currentPosition();
        Serial.println(pos);
       }

    else if (command.startsWith("P=")) {

       // split the value from the command here and change the parameter accordingly
       float current_position = command.substring(command.indexOf('=')+1).toInt();
       stepper.setCurrentPosition(current_position);
       long pos = stepper.currentPosition();
       Serial.println(pos);
       }

    else if (command == "TP?") {
       long pos = stepper.targetPosition();
       Serial.println(pos);
       }

    else if (command.startsWith("TP=")) {
       long set_position = command.substring(command.indexOf('=')+1).toInt();
       long pos = stepper.currentPosition();
       
       if (limit_switch_state == false)
       {
         stepper.moveTo(set_position);
       }       
       else if (limit_switch_state_lower && (set_position > pos))
       {
         stepper.moveTo(set_position);
       }
       
       else if (limit_switch_state_upper && (set_position < pos))
       {
         stepper.moveTo(set_position);
       }

       long position = stepper.targetPosition();
       Serial.println(position);
       }

    else if (command.startsWith("RP=")) {
       
       long set_position = command.substring(command.indexOf('=')+1).toInt() + stepper.targetPosition();
       long pos = stepper.currentPosition();
       
       if (limit_switch_state == false)
       {
         stepper.moveTo(set_position);
       }       
       else if (limit_switch_state_lower && (set_position > pos))
       {
         stepper.moveTo(set_position);
       }
       else if (limit_switch_state_upper && (set_position < pos))
       {
         stepper.moveTo(set_position);
       }
       else
       {
         Serial.println(limit_switch_state_upper);
         Serial.println((set_position < pos));
         Serial.println(limit_switch_state_upper && (set_position < pos));
       }

       long position = stepper.targetPosition();
       Serial.println(position);
       }

    else if (command == "A?") {
        float acceleration = stepper.acceleration();
        Serial.println(acceleration);
       }

    else if (command.startsWith("A=")) {

       // split the value from the command here and change the parameter accordingly
       float set_acceleration = command.substring(command.indexOf('=')+1).toFloat();
       stepper.setAcceleration(set_acceleration);
       float acceleration = stepper.acceleration();
       Serial.println(acceleration);
       }

    else if (command == "S?") {
        float speed = stepper.maxSpeed();
        Serial.println(speed);
       }

    else if (command.startsWith("S=")) {

       // split the value from the command here and change the parameter accordingly
       float set_speed = command.substring(command.indexOf('=')+1).toFloat();
       stepper.setMaxSpeed(set_speed);
       stepper.setSpeed(set_speed);
       float speed = stepper.maxSpeed();
       Serial.println(speed);
       }

    else if (command == "RUN") {
        stepper.run();
        Serial.println(command);
       }

    // else if (command == "DIR") {
    //     Serial.println();
    //    }

    else if (command == "STOP") {
        stepper.stop();
        stepper.setSpeed(0);
        stepper.runSpeed();
        Serial.println(command);
       }

    else if(command == "SOFTSTOP") {
      stepper.stop();
      Serial.println(command);
    }

    else if (command == "HOME") {
        // Serial.println(command);
        on_home();
        Serial.println(command);
     }

    else if (command == "MT?") {
        Serial.println(motor_driver_type);
     }

    else if (command.startsWith("MT=")) {

       // split the value from the command here and change the parameter accordingly
       motor_driver_type = command.substring(command.indexOf('=')+1).toInt();

       if (motor_driver_type == 1){
         AccelStepper stepper(motor_driver_type, motor_pin1,  motor_pin2); 
       }
       else {
         AccelStepper stepper(motor_driver_type, motor_pin1,  motor_pin2, motor_pin3,  motor_pin4); 
       }
          Serial.println(motor_driver_type);
       }

    else if (command == "SAVE") {
        long position_saved;
        EEPROM.get(0, position_saved);
        long position_to_save = stepper.currentPosition();
        if (position_to_save != position_saved){
          EEPROM.put(0, position_to_save);  // only write to EEPROM if necessary
        }
        Serial.println(position_to_save);
     }

    else if (command == "LOAD") {
        long position_to_load;
        EEPROM.get(0, position_to_load);
        stepper.setCurrentPosition(position_to_load);
        Serial.println(position_to_load);
     }

    else if (command == "HS?") {
        Serial.println(homing_speed);
     }

    else if (command.startsWith("HS=")) {
        homing_speed = command.substring(command.indexOf('=')+1).toInt();
        Serial.println(homing_speed);
     }

     // Request lower limit switch
    else if (command == "LL?") {
        limit_switch_state_lower = digitalRead(limit_switch_pin_lower);
        Serial.println(limit_switch_state_lower);
       }

     // Request uppwer limit switch
    else if (command == "LU?") {
        limit_switch_state_upper = digitalRead(limit_switch_pin_upper);
        Serial.println(limit_switch_state_upper);
       }    

    else if (command.startsWith("SC=")) {

      // split the value from the command here and change the parameter accordingly
      limit_switch_config = command.substring(command.indexOf('=')+1).toInt();

      if (limit_switch_config == 0){
        activate_lower_switch = false;
        activate_upper_switch = false;
      }
      else if (limit_switch_config == 1){
        activate_lower_switch = true;
        activate_upper_switch = false;
      }
      else if (limit_switch_config == 2){
        activate_lower_switch = false;
        activate_upper_switch = true;
      }
      else if (limit_switch_config == 3){
        activate_lower_switch = true;
        activate_upper_switch = true;
      }
      else {
        Serial.println("Limit switch config code out of range: " + limit_switch_config);
      }
      Serial.println(limit_switch_config);
      }

    else if (command.startsWith("SC?")) {
      Serial.println(limit_switch_config);
    }

    else 
     {
     Serial.println("Unknown command: " + command);
     }
     
   }
}
