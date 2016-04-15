// ----------------------------------------------------------------------------
// Callbacks.cpp
//
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------
#include "Callbacks.h"


namespace callbacks
{

SerialReceiver& serial_receiver = controller.getSerialReceiver();

IndexedContainer<PatternInfo,constants::INDEXED_PATTERNS_COUNT_MAX> indexed_patterns;

void startPwmCallback()
{
  int relay = serial_receiver.readInt(1);
  long period = serial_receiver.readLong(2);
  long on_duration = serial_receiver.readLong(3);
  EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(callbacks::closeRelayEventCallback,
                                                                             callbacks::openRelayEventCallback,
                                                                             constants::delay,
                                                                             period,
                                                                             on_duration,
                                                                             relay);
}

void startPwmPatternCallback()
{
  if (indexed_patterns.full())
  {
    return;
  }
  int relay = serial_receiver.readInt(1);
  long pwm_period = serial_receiver.readLong(2);
  long pwm_on_duration = serial_receiver.readLong(3);
  long pattern_period = serial_receiver.readLong(4);
  long pattern_on_duration = serial_receiver.readLong(5);
  PatternInfo pattern_info;
  pattern_info.relay = relay;
  pattern_info.pwm_period = pwm_period;
  pattern_info.pwm_on_duration = pwm_on_duration;
  int index = indexed_patterns.add(pattern_info);
  EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(callbacks::startPwmEventCallback,
                                                                             callbacks::stopPwmEventCallback,
                                                                             constants::delay,
                                                                             pattern_period,
                                                                             pattern_on_duration,
                                                                             index);
}

void stopAllPwmCallback()
{
  EventController::event_controller.removeAllEvents();
  indexed_patterns.clear();
  controller.openAllRelays();
}

// EventController Callbacks
void closeRelayEventCallback(int relay)
{
  controller.closeRelay(relay);
}

void openRelayEventCallback(int relay)
{
  controller.openRelay(relay);
}

void startPwmEventCallback(int index)
{
  int relay = indexed_patterns[index].relay;
  long period = indexed_patterns[index].pwm_period;
  long on_duration = indexed_patterns[index].pwm_on_duration;
  indexed_patterns[index].event_id_pair =
    EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(callbacks::closeRelayEventCallback,
                                                                               callbacks::openRelayEventCallback,
                                                                               0,
                                                                               period,
                                                                               on_duration,
                                                                               relay);
}

void stopPwmEventCallback(int index)
{
  EventController::event_controller.removeEventPair(indexed_patterns[index].event_id_pair);
  controller.openRelay(indexed_patterns[index].relay);
}

}
