#include <Adafruit_MCP4728.h>

Adafruit_MCP4728 working_mcp;
Adafruit_MCP4728 mcp0;
Adafruit_MCP4728 mcp1;
Adafruit_MCP4728 mcp2;
Adafruit_MCP4728 mcp3;
Adafruit_MCP4728 mcp4;
Adafruit_MCP4728 mcp5;
Adafruit_MCP4728 mcp6;
Adafruit_MCP4728 mcp7;

Adafruit_MCP4728 mcp_list[8] = {
  mcp0,
  mcp1,
  mcp2,
  mcp3,
  mcp4,
  mcp5,
  mcp6,
  mcp7,
};

bool mcp_is_initialized[8] = {
  false,
  false,
  false,
  false,
  false,
  false,
  false,
  false,
};

uint8_t addresses[8] = {
  0x60,
  0x61,
  0x62,
  0x63,
  0x64,
  0x65,
  0x66,
  0x67,
};

String command;

channel channels[4] = {
  MCP4728_CHANNEL_A,
  MCP4728_CHANNEL_B,
  MCP4728_CHANNEL_C,
  MCP4728_CHANNEL_D,
};

int v_ref = MCP4728_VREF_VDD;
int v_gain = MCP4728_GAIN_1X;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  // Initliazation finished
  Serial.println("Ready");
}


void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0) {

    command = Serial.readStringUntil('\n'); // make sure you have '\n', "\n" does not work
    command.toUpperCase();  // commands are not case-sensitive
    command.replace(" ", "");  // removes all white spaces

    // Connect MCP with specific I2C Address (0-7)
    if (command.startsWith("AD=")) {
      int address = command.substring(command.indexOf('=')+1).toInt();
      set_mcp(address);
    }

    // Set Value for Channel: e.g. CH4=1000
    else if (command.startsWith("CH")) {
      int channel = command.substring(command.indexOf('H')+1, command.indexOf('=')).toInt();
      int voltage = command.substring(command.indexOf('=')+1).toInt();

      set_voltage(channel, voltage);
    }

    // Set Reference Voltage: VR=E or VR=I (external or internal)
    else if (command.startsWith("VR")) {
      String source = command.substring(command.indexOf('=')+1);
      set_vref(source);
    }

    // Set Gain for internal reference voltage: GN=1 or GN=2 (1X or 2X)
    else if (command.startsWith("GN")) {
      int gain = command.substring(command.indexOf('=')+1).toInt();
      set_gain(gain);
    }
  }
}

// ------------- Initialize MCP ------------------------
void set_mcp(int address) {
  // If the MCP is not started yet, initialize new 
  if (!mcp_is_initialized[address]) {
    if (!mcp_list[address].begin(addresses[address])) {
    // Initialization Failed
    Serial.print("NAK");
    Serial.println(address);
    }
    else {
      // Initialization Succesfull 
      mcp_is_initialized[address] = true;

      // Assign working_mcp to it
      working_mcp = mcp_list[address];
      
      Serial.print("ACK");
      Serial.println(address);
    }
  }
  else {
    // If the MCP is already initialized, set working_mcp
    working_mcp = mcp_list[address];
    Serial.print("ACK");
    Serial.println(address);
  }
}

// ------------- Set Voltage ------------------------
void set_voltage(int channel, int voltage) {
  if (channel > 3 || voltage > 4095 || voltage < 0) {
    // Maximum 4 channels, Prevent overflow of voltage.
    Serial.println("NAK");
  }
  else {
    working_mcp.setChannelValue(channels[channel], voltage, v_ref, v_gain);
    Serial.print("ACK");
    Serial.print(channel);
    Serial.print("=");
    Serial.println(voltage);
  }
}

// ------------- Set Reference ------------------------
void set_vref(String source) {
  if (source == "E") {
    v_ref = MCP4728_VREF_VDD;
    Serial.println("ACKE");
  } 
  else if (source == "I") {
    v_ref = MCP4728_VREF_INTERNAL;
    Serial.println("ACKI");
  }
  else {
    Serial.println("NAK");
  }
}

// ------------- Set Gain ------------------------
void set_gain(int gain) {
  if (gain == 1) {
    v_gain = MCP4728_GAIN_1X;
    Serial.println("ACK1");
  } 
  else if (gain == 2) {
    v_gain = MCP4728_GAIN_2X;
    Serial.println("ACK2");
  }
  else {
    Serial.println("NAK");
  }
}
