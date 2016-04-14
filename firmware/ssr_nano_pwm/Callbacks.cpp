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
// EventController Callbacks
void closeRelayEventCallback(int relay)
{
  controller.closeRelay(relay);
}

void openRelayEventCallback(int relay)
{
  controller.openRelay(relay);
}

}
