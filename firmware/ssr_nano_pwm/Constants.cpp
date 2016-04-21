// ----------------------------------------------------------------------------
// Constants.cpp
//
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------
#include "Constants.h"


namespace constants
{
const unsigned int baudrate = 9600;

const uint8_t relay_pins[RELAY_COUNT] = {2,3,4,5,6,7,8,9};
const uint8_t high_freq_relay_pins[HIGH_FREQ_RELAY_COUNT] = {3,9};

}
