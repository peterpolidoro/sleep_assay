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

#include "Streaming.h"

namespace callbacks
{
// EventController Callbacks
void closeRelayEventCallback(int relay);

void openRelayEventCallback(int relay);

}
#endif
