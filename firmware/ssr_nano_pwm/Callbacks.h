// ----------------------------------------------------------------------------
// Callbacks.h
//
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------
#ifndef CALLBACKS_H
#define CALLBACKS_H
#include "Constants.h"
#include "Controller.h"

#include "EventController.h"
#include "IndexedContainer.h"
#include "Streaming.h"

namespace callbacks
{
struct PatternInfo
{
  int relay;
  long pwm_period;
  long pwm_on_duration;
  int power;
  EventController::EventIdPair event_id_pair;
};

void startPwmCallback();

void startPwmPatternCallback();

void startPwmPatternPowerCallback();

void stopAllPwmCallback();

// EventController Callbacks
void closeRelayEventCallback(int relay);

void openRelayEventCallback(int relay);

void startPwmEventCallback(int index);

void startPwmPowerEventCallback(int index);

void stopPwmEventCallback(int index);

}
#endif
