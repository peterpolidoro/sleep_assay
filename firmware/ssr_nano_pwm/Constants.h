// ----------------------------------------------------------------------------
// Constants.h
//
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------
#ifndef CONSTANTS_H
#define CONSTANTS_H
#include "ConstantVariable.h"


namespace constants
{
enum{RELAY_COUNT=8};
enum{INDEXED_PATTERNS_COUNT_MAX=4};

enum
  {
    METHOD_ID_START_PWM,
    METHOD_ID_START_PWM_PATTERN,
    METHOD_ID_STOP_ALL_PULSES,
  };

extern const unsigned int baudrate;

extern const uint8_t ssr_pins[RELAY_COUNT];

}
#endif
