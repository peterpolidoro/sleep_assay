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
}

void Controller::openRelay(int relay)
{
  digitalWrite(constants::relay_pins[relay],LOW);
}

void Controller::pwmRelay(int relay, uint8_t duty_cycle)
{
  analogWrite(constants::relay_pins[relay],value);
}

void Controller::openAllRelays()
{
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    openRelay(relay);
  }
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
    default:
      break;
  }
}

Controller controller;
