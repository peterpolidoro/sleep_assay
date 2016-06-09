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
  void setRelayPower(int relay, int power);
  void openAllRelays();
  void setPwmStatusRunning(int relay, int level);
  void setPwmStatusStopped(int relay, int level);
  void setAllPwmStatusStopped();
  int getPower(int relay);
  constants::PwmStatus getPwmStatus(int relay, int level);
private:
  SerialReceiver serial_receiver_;
  int power_[constants::RELAY_COUNT];
  constants::PwmStatus pwm_status_[constants::RELAY_COUNT][constants::PWM_LEVEL_COUNT_MAX];
  void processMessage();
};

extern Controller controller;

#endif
