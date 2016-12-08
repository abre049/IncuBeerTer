// IncuBeertor
// Dependables
//#include <Time.h> // time.h isn't available on circuit.io but this will go into the real thing
#include <OneWire.h>
#include <DallasTemperature.h> // http://arduino-info.wikispaces.com/Brick-Temperature-DS18B20 is a very useful reasorce
#include <SoftwareSerial.h>

// constants
//const int nmos = 3; 
const int peltierRelay1Pin = 8;
const int peltierRelay2Pin = 10;
const int fanRelayPin = 4;
const int tempPin = A1;
const int pumpPin = 5;
const int ledPin = 13;
const int btTxPin = 12; //transmit to the rx of bluetooth
const int btRxPin = 11; //recieve from Tx of bluetooth

DeviceAddress Probe1Addr = {0x28, 0x4D, 0x8D, 0x6E, 0x05, 0x00, 0x00, 0xB6};
DeviceAddress Probe2Addr = {0x28, 0xBB, 0x29, 0x09, 0x06, 0x00, 0x00, 0xA8}; //This is the old probe used in the original temperatuer control/
SoftwareSerial btSerial(btRxPin, btTxPin); //Rx, Tx

OneWire oneWire(tempPin); // Setup a oneWire instance to communicate with any OneWire devices
DallasTemperature sensors(&oneWire);// Pass our oneWire reference to Dallas Temperature. 

// user adjustable variables
//float targetTempArray[] = {25.0};
//float targetTempTimeArray[] = {0};
float tempDev = 1.0;

// non pin constants
//const int time0 = now(); // now() required time.h which will be present in real thing to control chaning target temps over time

//global variables
float temp1 = 0.0;
float temp2 = 0.0;
float tempAve = 0.0;
String peltierState = "OFF";
boolean toggle = 0;
float targetTemp = 0.0;

void setup() {
  // initialize the digital pin as an output.
//  pinMode(nmos, OUTPUT);
  pinMode(peltierRelay1Pin, OUTPUT);
  pinMode(peltierRelay2Pin, OUTPUT);
  pinMode(fanRelayPin, OUTPUT);
  pinMode(pumpPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  
  
  Serial.begin(9600); // will need to be 57600 when using bluetooth
  btSerial.begin(57600);

  sensors.setResolution(Probe1Addr, 12);
  sensors.setResolution(Probe2Addr, 12);

  hold();
  digitalWrite(ledPin, LOW);
}

void heat() {
//  Heats the side with writing which will be on the water side
  digitalWrite(peltierRelay1Pin, LOW);
  digitalWrite(peltierRelay2Pin, HIGH);
  digitalWrite(fanRelayPin, HIGH); // fan and pump on note that the fan is on when low. also need a resistor between pin and gnd to turn off when not in use
  digitalWrite(pumpPin, HIGH);
  peltierState = "HEAT";
  digitalWrite(ledPin, HIGH);
}

void cool() {
//  Cools the side with writing which will be on the water side
  digitalWrite(peltierRelay1Pin, HIGH);
  digitalWrite(peltierRelay2Pin, LOW);
  digitalWrite(fanRelayPin, HIGH); // fan on
  digitalWrite(pumpPin, HIGH);
  peltierState = "COOL";
  digitalWrite(ledPin, LOW);
}

void hold() {
//  Turns the Peltiers off
  digitalWrite(peltierRelay1Pin, LOW);
  digitalWrite(peltierRelay2Pin, LOW);
  digitalWrite(fanRelayPin, LOW);
  digitalWrite(pumpPin, LOW);
  peltierState = "OFF";
  digitalWrite(ledPin, LOW);
}

boolean isFloat(String proband){
  boolean noLetters = true;
  for (int idx; idx < proband.length(); idx++){
    if (proband.charAt(idx)!= '.' || !isDigit(proband.charAt(idx))){
      noLetters = false;     
    }
  }
  return noLetters;
}



void loop() {
  sensors.requestTemperatures();
  temp1 = sensors.getTempC(Probe1Addr); // -0.06 adjusted so that probes read the same at roome temperature (was 0.12 degrees different)
  temp2 = sensors.getTempC(Probe2Addr); // +0.06 adjusted so that probes read the same at roome temperature (was 0.12 degrees different)
  tempAve = (temp1+temp2) * 0.5;

//  Serial.println("T1: " + String(temp1) + ", T2: " + String(temp2) + ", tempAve" + String(tempAve));
//  heat();
//  Serial.println("heating");
//  delay(2000);
//  cool();
//  Serial.println("cooling");
//  delay(2000);
//  hold();
//  Serial.println("holding");
//  delay(2000);
  
//  if(btSerial.available()){
//    String newTargetTemp;
//    delay(3); //allow buffer to fill
//    
//    if (btSerial.available() >0) {
//      newTargetTemp = btSerial.readString();      
//      targetTemp = newTargetTemp.toFloat();
//    }

  if(btSerial.available()){
    String newTargetTemp;
    delay(50); //allow buffer to fill
    
    if (btSerial.available() >0) {
      String msgIn = btSerial.readString();
      String firstHalf = msgIn.substring(0,(msgIn.length()/2));
      String secondHalf = msgIn.substring(msgIn.length()/2);
      if (firstHalf == secondHalf){
        newTargetTemp = firstHalf;
        Serial.println("new tt: "+newTargetTemp); 
  
        if (isFloat(newTargetTemp)){
          targetTemp = newTargetTemp.toFloat();
        }
      
        Serial.println("old tt: "+String(targetTemp));
    
        if(tempAve > (targetTemp+tempDev)){
          cool();
        } else if(tempAve < (targetTemp - tempDev)){
          heat();
        } else {hold();}

        String msgOut = ",tt" + String(targetTemp) + ";,t1" + String(temp1) + ";,t2" + String(temp2) + ";,st" + peltierState+";";
        msgOut = msgOut+msgOut;
        Serial.println(msgOut);
        
        btSerial.println(msgOut);
        btSerial.flush();
      }
    }
  }
}


