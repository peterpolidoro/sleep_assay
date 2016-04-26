// ----------------------------------------------------------------------------
// Controller.cpp
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------
#include "Controller.h"


Controller::Controller()
{
}

void Controller::setup()
{
  EventController::event_controller.setup();

  // Pin Setup
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    pinMode(constants::relay_pins[relay],OUTPUT);
    openRelay(relay);
  }
  setAllPwmStatusStopped();

  // Setup Streams
  Serial.begin(constants::baudrate);

}

void Controller::update()
{
  // Check if message is available
  while (Serial.available() > 0)
  {
    serial_receiver_.process(Serial.read());
    if (serial_receiver_.messageReady())
    {
      processMessage();
      serial_receiver_.reset();
    }
  }
}

SerialReceiver& Controller::getSerialReceiver()
{
  return serial_receiver_;
}

void Controller::closeRelay(int relay)
{
  digitalWrite(constants::relay_pins[relay],HIGH);
  power_[relay] = constants::power_max;
}

void Controller::openRelay(int relay)
{
  digitalWrite(constants::relay_pins[relay],LOW);
  power_[relay] = constants::power_min;
}

void Controller::highFreqPwmRelay(int relay, int power)
{
  analogWrite(constants::relay_pins[relay],power);
  power_[relay] = power;
}

void Controller::openAllRelays()
{
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    openRelay(relay);
  }
}

void Controller::setPwmStatusRunning(int relay)
{
  pwm_status_[relay] = constants::PWM_RUNNING;
}

void Controller::setPwmStatusStopped(int relay)
{
  pwm_status_[relay] = constants::PWM_STOPPED;
}

void Controller::setAllPwmStatusStopped()
{
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    setPwmStatusStopped(relay);
  }
}

int Controller::getPower(int relay)
{
  return power_[relay];
}

constants::PwmStatus Controller::getPwmStatus(int relay)
{
  return pwm_status_[relay];
}

void Controller::processMessage()
{
  int method_id;

  method_id = serial_receiver_.readInt(0);

  switch (method_id)
  {
    case constants::METHOD_ID_START_PWM:
      callbacks::startPwmCallback();
      break;
    case constants::METHOD_ID_START_PWM_PATTERN:
      callbacks::startPwmPatternCallback();
      break;
    case constants::METHOD_ID_START_PWM_PATTERN_POWER:
      callbacks::startPwmPatternPowerCallback();
      break;
    case constants::METHOD_ID_STOP_ALL_PULSES:
      callbacks::stopAllPwmCallback();
      break;
    case constants::METHOD_ID_GET_POWER:
      callbacks::getPowerCallback();
      break;
    case constants::METHOD_ID_GET_PWM_STATUS:
      callbacks::getPwmStatusCallback();
      break;
    default:
      break;
  }
}

Controller controller;
