#include "Streaming.h"

#include "SerialReceiver.h"

#include "Constants.h"
#include "Callbacks.h"
#include "Controller.h"

#include "TimerOne.h"
#include "EventController.h"


// See README.md for more information

void setup()
{
  controller.setup();
}

void loop()
{
  controller.update();
}
