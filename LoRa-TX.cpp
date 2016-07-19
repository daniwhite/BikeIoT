// Feather9x_TX

#include <iostream>
#include <SPI.h>
#include <RH_RF95.h>
using namespace std;

/* for feather32u4 */
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 7

/* for feather m0
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3
*/

/* for shield
#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 7
*/

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup()
{
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  cout << "Feather LoRa TX Test!" << endl;

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  usleep(10000);
  digitalWrite(RFM95_RST, HIGH);
  usleep(10000);

  while (!rf95.init()) {
    cout << "LoRa radio init failed" << endl;
    while (1);
  }
  cout << "LoRa radio init OK!" << endl;

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    cout << "setFrequency failed" << endl;
    while (1);
  }
  cout << "Set Freq to: " << RF95_FREQ << endl;

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
}

int16_t packetnum = 0;  // packet counter, we increment per xmission

void loop()
{
  cout << "Sending to rf95_server");
  // Send a message to rf95_server

  char radiopacket[20] = "Hello World #      ";
  itoa(packetnum++, radiopacket+13, 10);
  cout << "Sending " << radiopacket << endl;
  radiopacket[19] = 0;

  cout << "Sending..." << endl; usleep(10000);
  rf95.send((uint8_t *)radiopacket, 20);

  cout << "Waiting for packet to complete..." << endl; usleep(10000);
  rf95.waitPacketSent();
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  cout << "Waiting for reply..."); usleep(10000);
  if (rf95.waitAvailableTimeout(1000))
  {
    // Should be a reply message for us now
    if (rf95.recv(buf, &len))
   {
      cout << "Got reply: " << (char*)buf) << endl;
      cout << "RSSI: " << rf95.lastRssi() << endl;
    }
    else
    {
      cout << "Receive failed");
    }
  }
  else
  {
    cout << "No reply, is there a listener around?");
  }
  usleep(1000000);
}
