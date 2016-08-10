#define DATA_POINTS 4
#define DELIM ','

void getDataArr(String* data);
String getData();
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
    Serial.println(data);
    Particle.publish("Brdcst",data);
  }
}

void getDataArr(String* data) {
  for (int i = 0; i < DATA_POINTS;i++) {
    bool delimFound = false;
    String datapoint = "";
    // Check if we run into the delimiter or if there's nothing left on serial
    while(!delimFound && Serial.available() > 0) {
      char nextByte = Serial.read();
      if (nextByte == DELIM) {
        delimFound = true;
      } else {
        datapoint += nextByte;
      }
    }
    data[i] = datapoint;
  }
  Serial.write("OK\r\n");
  return;
}

String getData() {
  String data = "";
  while(Serial.available() > 0) {
    char nextByte = Serial.read();
    data += nextByte;
    }
  Serial.write("OK\r\n");
  return data;
}
