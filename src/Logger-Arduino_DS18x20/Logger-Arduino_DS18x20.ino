// code taken from
// https://create.arduino.cc/projecthub/TheGadgetBoy/ds18b20-digital-temperature-sensor-and-arduino-9cc806
// https://draeger-it.blog/arduino-lektion-48-temperatursensor-ds18b20/

// created by Axel Fischer
// last version change: 06.09.21


/********************************************************************/
// First we include the libraries
#include <OneWire.h> // tested with version 2.3.5
#include <DallasTemperature.h> // tested with version 3.9.0


/********************************************************************/
// Data wire is plugged into pin 2 on the Arduino 
#define ONE_WIRE_BUS 2
/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices  
// (not just Maxim/Dallas temperature ICs) 
OneWire oneWire(ONE_WIRE_BUS); 
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);
/********************************************************************/ 

String command;  
int sensorCount;
bool waitForConversion;
DeviceAddress tempDeviceAddress;                       
 
void setup() {
  
  Serial.begin(9600);

  sensors.begin();

  sensorCount = sensors.getDS18Count();

  sensors.setWaitForConversion(false);
  Serial.println("Arduino DS18x20 started");
                               
}
 
void loop() {

  if (waitForConversion == 0){
    sensors.requestTemperatures(); // updating the temperature whenever there is no request, so that the temperature is actual as possible if waitForConversion is switched off
  }

  if (Serial.available()) {
      command = Serial.readStringUntil('\n');
      
      if (command == "ReadC?") {
          if (waitForConversion == 1){
            sensors.requestTemperatures();
          }
          String response = "";
          for(int i=0;i<sensorCount;i++){

            if (i > 0) {
              response = response + ",";
              }

            response = response + sensors.getTempCByIndex(i);
            }
          Serial.println(response);
          
        }

      else if (command == "ReadF?") {
          if (waitForConversion == 1){
            sensors.requestTemperatures();
          }
          String response = "";
          for(int i=0;i<sensorCount;i++){

            if (i > 0) {
              response = response + ",";
              }

            response = response + sensors.getTempFByIndex(i);
            }
          Serial.println(response);
        }

        else if (command == "Sensors?") {
            sensorCount = sensors.getDS18Count();
            Serial.println(sensorCount);
        }

        else if (command == "Resolution?") {
            int res = sensors.getResolution();
            Serial.println(res);
        }

        else if (command.startsWith("Resolution=")) {

            int resolution = command.substring(command.indexOf('=')+1).toInt();
            
            for(int i=0;i<sensorCount;i++){
              char address = sensors.getAddress(tempDeviceAddress, i);
              int res = sensors.setResolution(tempDeviceAddress, resolution);
              
            }
            Serial.println(resolution);
        }

        else if (command == "Addresses?") {

            for(int i=0;i<sensorCount;i++){
              char address = sensors.getAddress(tempDeviceAddress, i);

              for (uint8_t i = 0; i < 8; i++)
                {
                  if (tempDeviceAddress[i] < 16) Serial.print("0");  // this adds a 0 before any hex number below 16 that is represented by a single character 0-f
                  Serial.print(tempDeviceAddress[i], HEX);
                }
              Serial.println();
            }
          
        }

       else if (command == "WaitForConversion?") {

             bool waitForConversion = sensors.getWaitForConversion();

             if (waitForConversion == true) {
               Serial.println("1");
             }
             else if (waitForConversion == false) {
               Serial.println("0");
             }
        }

        else if (command.startsWith("WaitForConversion=")) {

            int state = command.substring(command.indexOf('=')+1).toInt();

            if (state == 0) {
                sensors.setWaitForConversion(false);
                Serial.println(state);
            }
            else if (state == 1) {
              sensors.setWaitForConversion(true);
              Serial.println(state);
            }

            else {
              Serial.println("Given state is not defined for WaitForConversion");
            }

            
            
        }

        

        else {
          Serial.println("Command unknown: " + command);
          
        }



//      if (command.startsWith("Pin")) {
//          Serial.println(command);   
//          String pin = command.substring(3);
//          Serial.println(pin.toInt());
//        }

        
  }

   


    
}
