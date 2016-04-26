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
enum{HIGH_FREQ_RELAY_COUNT=2};
enum{INDEXED_PATTERNS_COUNT_MAX=4};

enum
  {
    METHOD_ID_START_PWM,
    METHOD_ID_START_PWM_PATTERN,
    METHOD_ID_START_PWM_PATTERN_POWER,
    METHOD_ID_STOP_ALL_PULSES,
    METHOD_ID_GET_POWER,
    METHOD_ID_GET_PWM_STATUS,
  };

enum PwmStatus
  {
    PWM_STOPPED=0,
    PWM_RUNNING=1,
  };

extern const unsigned int baudrate;

extern const uint8_t relay_pins[RELAY_COUNT];
extern const uint8_t high_freq_relay_pins[HIGH_FREQ_RELAY_COUNT];

extern const int power_min;
extern const int power_max;

}
#endif
