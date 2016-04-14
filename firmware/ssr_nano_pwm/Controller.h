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
  void closeRelay(int relay);
  void openRelay(int relay);
private:
  SerialReceiver serial_receiver_;
  void processMessage();
  void startPwm(int relay,long period,long on_duration);
  void stopAllPwm();
};

extern Controller controller;

#endif
