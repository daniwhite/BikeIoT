#define DATA_POINTS 4
#define DELIM ','

String getData();
void sendResponse();
bool broadcast;

void setup() {
  Serial.begin(115200);
  broadcast = true;
}

// Note: Code that blocks for too long (like more than 5 seconds), can make weird things happen (like dropping the network connection).  The built-in delay function shown below safely interleaves required background activity, so arbitrarily long delays can safely be done if you need them.


void loop() {
  String data;
  if (Serial.available() > 0) {
    data = getData();
    if (data == "Cell on") {
      Cellular.on();
      Serial.println("Cell on");
    } else if (data == "Cell off") {
      Cellular.off();
      Serial.println("Cell off");
    } else {
      Particle.publish("Brdcst", data);
    }
    sendResponse();
  }
}

String getData() {
  String data = "";
  while(Serial.available() > 0) {
    char nextByte = Serial.read();
    data += nextByte;
    }
  return data;
}

void sendResponse(){
  Serial.write("OK\r\n");
  return;
}
