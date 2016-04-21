// ----------------------------------------------------------------------------
// Controller.h
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------

#ifndef CONTROLLER_H
#define CONTROLLER_H
#include "SerialReceiver.h"
#include "TimerOne.h"
#include "EventController.h"
#include "Constants.h"
#include "Callbacks.h"

class Controller
{
public:
  Controller();
  void setup();
  void update();
  SerialReceiver& getSerialReceiver();

  void closeRelay(int relay);
  void openRelay(int relay);
  void pwmRelay(int relay, uint8_t duty_cycle);
  void openAllRelays();
private:
  SerialReceiver serial_receiver_;
  void processMessage();
};

extern Controller controller;

#endif
