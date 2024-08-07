
String command;
String answer;
String EOL;

void setup() {

   for (int pin=2; pin < NUM_DIGITAL_PINS; pin++){
    pinMode(pin, INPUT);
   }

   Serial.begin(115200);
   Serial.setTimeout(100);
   Serial.println("Arduino AllPins In");
}

void loop() {

  if (Serial.available()) {
    
    command = Serial.readStringUntil('\n');

    
    if (command.startsWith("R")) {
      // Expects command starting with R followed by channel number and analog/digital key
      // Example: R2D,12D,0A,1A,\n

      String channel;
      
      // Skip first letter
      for (int i = 1; i < command.length(); i++) {
        char c = command.charAt(i);

        // Digital Pin detected
        if (c == 'D') {
          Serial.print(digitalRead(channel.toInt()));
          Serial.print(",");
          channel = "";
        }
        // Analog Pin detected
        else if (c == 'A') {
          Serial.print(analogRead(channel.toInt()));
          Serial.print(",");
          channel = "";
        }
        // Deliminter
        else if (c == ',') {
          channel = "";
        }
        // Read out channel
        else {
          channel += c;
        }
      }
      // End measurement sequence
      Serial.print("\n");
   }

  }
}
