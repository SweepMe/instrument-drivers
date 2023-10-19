#include "DHT.h" //DHT Bibliothek laden

//#define DHTPIN 2 //Der Sensor wird an PIN 2 angeschlossen    
  
//#define DHTTYPE DHT22    // DHT11 or DHT22

int DHTPIN = 2; // change to your pin used to read out the sensing value
int DHTTYPE = 22; // choose between 11 (DHT11) or 22 (DHT22)

  
DHT dht(DHTPIN, DHTTYPE);

float humidity, temperature;
String command;                           
int var = 0;
 
void setup() {
  
  Serial.begin(9600);

//  while (var == 0) {
//     if (Serial.available()) {
//        command = Serial.readString();
//       
//        if (command == "DHT\n") {
//          Serial.print(command);
//          break;
//          }
//      }
//    }

  dht.begin();  
  Serial.println("Arduino DHTxx Sensor");
                                          
}
 
void loop() {

  if (Serial.available()) {
      command = Serial.readStringUntil('\n');
      
      if (command == "Read?") {
          Serial.println(command);
          
          humidity = dht.readHumidity();                           
          temperature = dht.readTemperature();
          Serial.print(humidity);
          Serial.print(",");
          Serial.println(temperature);
        
        }
  }
    
}
