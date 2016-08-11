#define DATA_POINTS 4
#define DELIM ','

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

String getData() {
  String data = "";
  while(Serial.available() > 0) {
    char nextByte = Serial.read();
    data += nextByte;
    }
  Serial.write("OK\r\n");
  return data;
}
