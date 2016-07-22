#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

static int cnt = 0;
static osjob_t init_job;

// Pin mapping
const lmic_pinmap lmic_pins = {
    .nss = 8,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 4,
    .dio = {1, 2, 3},
};

static void initfunc(osjob_t* job){
  Serial.println("Hello!");
  Serial.print("cnt = ");  Serial.println(cnt);
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
  os_setTimedCallback(job, os_getTime()+sec2osticks(1), initfunc);
}

void setup() {
  // put your setup code here, to run once:
  pinMode(13, OUTPUT);
  os_init();
  initfunc(&init_job);
}

void loop() {
  os_runloop();
  // put your main code here, to run repeatedly:

}
