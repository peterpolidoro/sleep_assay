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
struct PwmInfo
{
  int relay;
  int power;
  int level;
  int child_index;
  long period;
  long on_duration;
  EventController::EventIdPair event_id_pair;
};

void startPwmCallback();

void stopAllPwmCallback();

void getPowerCallback();

void getPwmStatusCallback();

// EventController Callbacks
void setParentPwmStatusRunningEventCallback(int index);

void removeParentAndChildren(int index);

void setParentPwmStatusStoppedEventCallback(int index);

void startPowerPwmEventCallback(int index);

void stopPwmEventCallback(int index);

}
#endif
