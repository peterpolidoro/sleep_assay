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
    pinMode(constants::ssr_pins[relay],OUTPUT);
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

void Controller::closeRelay(int relay)
{
  digitalWrite(constants::ssr_pins[relay],HIGH);
}

void Controller::openRelay(int relay)
{
  digitalWrite(constants::ssr_pins[relay],LOW);
}

void Controller::processMessage()
{
  int method_id;

  method_id = serial_receiver_.readInt(0);

  switch (method_id)
  {
    case constants::METHOD_ID_START_PWM:
      {
        int relay = serial_receiver_.readInt(1);
        long period = serial_receiver_.readLong(2);
        long on_duration = serial_receiver_.readLong(3);
        startPwm(relay,period,on_duration);
        break;
      }
    case constants::METHOD_ID_STOP_ALL_PULSES:
      {
        stopAllPwm();
        break;
      }
    default:
      break;
  }
}

void Controller::startPwm(int relay,long period,long on_duration)
{
  EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(callbacks::closeRelayEventCallback,
                                                                             callbacks::openRelayEventCallback,
                                                                             constants::delay,
                                                                             period,
                                                                             on_duration,
                                                                             relay);
}

void Controller::stopAllPwm()
{
  EventController::event_controller.removeAllEvents();
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    openRelay(relay);
  }
}

Controller controller;
