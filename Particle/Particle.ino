#define DATA_POINTS 3
#define DELIM ','

void getData(String* data);
void shareData(String* data);

void setup() {
  Cellular.off();
  Serial.begin(115200);
}

// Note: Code that blocks for too long (like more than 5 seconds), can make weird things happen (like dropping the network connection).  The built-in delay function shown below safely interleaves required background activity, so arbitrarily long delays can safely be done if you need them.

void loop() {
  if (Serial.available() > 0) {
    String data[DATA_POINTS];
    getData(data);
    for (int i = 0; i < DATA_POINTS; i++) {
      Serial.println(data[i]);
    }
  }
}

void getData(String* data) {
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

void shareData(String* data) {
  Particle.variable("loudness", data[0]);
  Particle.variable("temperature", data[1]);
  Particle.variable("humidity", data[2]);
}
