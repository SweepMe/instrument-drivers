
String command;
String answer;
String EOL;

void setup() {

   for (int i=2; i <= 13; i++){
  
    pinMode(i, INPUT);
   }

   pinMode(LED_BUILTIN, OUTPUT);

   digitalWrite(LED_BUILTIN, HIGH);
   delay(100);
   digitalWrite(LED_BUILTIN, LOW);

   Serial.begin(115200);
   Serial.setTimeout(100);
   Serial.println("Arduino AllPins In");
}

void loop() {

  if (Serial.available()) {
    
    command = Serial.readStringUntil('\n');

    if (command == "R") {

        for (int i=2; i <= 13; i++){

//          answer = answer + digitalRead(i) + ",";
          Serial.print(digitalRead(i));
          Serial.print(",");
        }
      
        for (int i=0; i <= 7; i++){

//          answer = answer + analogRead(i) + ",";
          Serial.print(analogRead(i));
          Serial.print(",");
        }

//        Serial.println(answer);
        Serial.print("\n");

   }

  }
}
