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
//MAX values must be >= 1, >= created/copied count, < RAM limit
enum{SAVED_VARIABLE_COUNT_MAX=1};
enum{PARAMETER_COUNT_MAX=15};
enum{METHOD_COUNT_MAX=30};

enum {STATE_COUNT=16};
enum {INDEXED_CHANNELS_COUNT_MAX=8};
enum {INDEXED_PULSES_COUNT_MAX=4};

extern const unsigned int baudrate;

extern const unsigned int model_number;

extern const unsigned char firmware_major;
extern const unsigned char firmware_minor;
extern const unsigned char firmware_patch;

extern const int cs_pin;
extern const int reset_pin;

extern const uint8_t channels_per_ic_count;
extern const uint8_t ic_count;
extern const uint8_t channel_count;

extern const uint8_t channel_min;
extern const uint8_t channel_max;

extern const uint32_t duration_min;
extern const uint32_t duration_max;

extern const float frequency_min;
extern const float frequency_max;

extern const uint8_t duty_cycle_min;
extern const uint8_t duty_cycle_max;

extern const uint32_t states_array_default[STATE_COUNT];

extern ConstantString device_name;

extern ConstantString duration_units_name;
extern ConstantString frequency_units_name;
extern ConstantString duty_cycle_units_name;

extern ConstantString states_name;

extern ConstantString channels_parameter_name;
extern ConstantString channel_parameter_name;
extern ConstantString state_parameter_name;
extern ConstantString delay_parameter_name;
extern ConstantString on_duration_parameter_name;
extern ConstantString period_parameter_name;
extern ConstantString count_parameter_name;
extern ConstantString frequency_parameter_name;
extern ConstantString duty_cycle_parameter_name;
extern ConstantString pwm_duration_parameter_name;
extern ConstantString spike_duty_cycle_parameter_name;
extern ConstantString spike_duration_parameter_name;
extern ConstantString hold_duty_cycle_parameter_name;
extern ConstantString hold_duration_parameter_name;
extern ConstantString pulse_wave_index_parameter_name;

extern ConstantString set_channel_on_method_name;
extern ConstantString set_channel_off_method_name;
extern ConstantString set_channels_on_method_name;
extern ConstantString set_channels_off_method_name;
extern ConstantString toggle_channel_method_name;
extern ConstantString toggle_channels_method_name;
extern ConstantString toggle_all_channels_method_name;
extern ConstantString set_all_channels_on_method_name;
extern ConstantString set_all_channels_off_method_name;
extern ConstantString set_channel_on_all_others_off_method_name;
extern ConstantString set_channel_off_all_others_on_method_name;
extern ConstantString set_channels_on_all_others_off_method_name;
extern ConstantString set_channels_off_all_others_on_method_name;
extern ConstantString get_channels_on_method_name;
extern ConstantString get_channels_off_method_name;
extern ConstantString get_channel_count_method_name;
extern ConstantString save_state_method_name;
extern ConstantString recall_state_method_name;
extern ConstantString get_saved_states_method_name;
extern ConstantString add_pulse_centered_method_name;
extern ConstantString add_pwm_period_on_duration_method_name;
extern ConstantString add_pwm_frequency_duty_cycle_method_name;
extern ConstantString add_spike_and_hold_method_name;
extern ConstantString stop_all_pulses_method_name;
extern ConstantString start_pwm_period_on_duration_method_name;
extern ConstantString start_pwm_frequency_duty_cycle_method_name;
extern ConstantString start_spike_and_hold_method_name;
extern ConstantString stop_pulse_wave_method_name;
}
#endif
