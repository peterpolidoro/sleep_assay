// ----------------------------------------------------------------------------
// Controller.cpp
//
// Authors:
// Peter Polidoro polidorop@janelia.hhmi.org
// ----------------------------------------------------------------------------
#include "Controller.h"


void Controller::setup()
{
  EventController::event_controller.setup();

  // Pin Setup

  // Device Info
  modular_server_.setName(constants::device_name);
  modular_server_.setModelNumber(constants::model_number);
  modular_server_.setFirmwareVersion(constants::firmware_major,constants::firmware_minor,constants::firmware_patch);

  // Add Server Streams
  modular_server_.addServerStream(Serial);

  // Set Storage
  modular_server_.setSavedVariableStorage(saved_variables_);
  modular_server_.setParameterStorage(parameters_);
  modular_server_.setMethodStorage(methods_);

  // Saved Variables
  modular_server_.createSavedVariable(constants::states_name,constants::states_array_default,constants::STATE_COUNT);

  // Parameters
  ModularDevice::Parameter& channel_parameter = modular_server_.createParameter(constants::channel_parameter_name);
  channel_parameter.setRange(constants::channel_min,constants::channel_max);

  ModularDevice::Parameter& channels_parameter = modular_server_.createParameter(constants::channels_parameter_name);
  channels_parameter.setTypeArray();
  channels_parameter.setRange(constants::channel_min,constants::channel_max);

  ModularDevice::Parameter& state_parameter = modular_server_.createParameter(constants::state_parameter_name);
  state_parameter.setRange(0,constants::STATE_COUNT-1);

  ModularDevice::Parameter& delay_parameter = modular_server_.createParameter(constants::delay_parameter_name);
  delay_parameter.setRange(constants::duration_min,constants::duration_max);
  delay_parameter.setUnits(constants::duration_units_name);

  ModularDevice::Parameter& on_duration_parameter = modular_server_.createParameter(constants::on_duration_parameter_name);
  on_duration_parameter.setRange(constants::duration_min,constants::duration_max);
  on_duration_parameter.setUnits(constants::duration_units_name);

  ModularDevice::Parameter& period_parameter = modular_server_.createParameter(constants::period_parameter_name);
  period_parameter.setRange(constants::duration_min,constants::duration_max);
  period_parameter.setUnits(constants::duration_units_name);

  ModularDevice::Parameter& count_parameter = modular_server_.createParameter(constants::count_parameter_name);
  count_parameter.setRange(constants::duration_min,constants::duration_max);

  ModularDevice::Parameter& frequency_parameter = modular_server_.createParameter(constants::frequency_parameter_name);
  frequency_parameter.setRange(constants::frequency_min,constants::frequency_max);
  frequency_parameter.setUnits(constants::frequency_units_name);

  ModularDevice::Parameter& duty_cycle_parameter = modular_server_.createParameter(constants::duty_cycle_parameter_name);
  duty_cycle_parameter.setRange(constants::duty_cycle_min,constants::duty_cycle_max);
  duty_cycle_parameter.setUnits(constants::duty_cycle_units_name);

  ModularDevice::Parameter& pwm_duration_parameter = modular_server_.createParameter(constants::pwm_duration_parameter_name);
  pwm_duration_parameter.setRange(constants::duration_min,constants::duration_max);
  pwm_duration_parameter.setUnits(constants::duration_units_name);

  ModularDevice::Parameter& spike_duty_cycle_parameter = modular_server_.createParameter(constants::spike_duty_cycle_parameter_name);
  spike_duty_cycle_parameter.setRange(constants::duty_cycle_min,constants::duty_cycle_max);
  spike_duty_cycle_parameter.setUnits(constants::duty_cycle_units_name);

  ModularDevice::Parameter& spike_duration_parameter = modular_server_.createParameter(constants::spike_duration_parameter_name);
  spike_duration_parameter.setRange(constants::duration_min,constants::duration_max);
  spike_duration_parameter.setUnits(constants::duration_units_name);

  ModularDevice::Parameter& hold_duty_cycle_parameter = modular_server_.createParameter(constants::hold_duty_cycle_parameter_name);
  hold_duty_cycle_parameter.setRange(constants::duty_cycle_min,constants::duty_cycle_max);
  hold_duty_cycle_parameter.setUnits(constants::duty_cycle_units_name);

  ModularDevice::Parameter& hold_duration_parameter = modular_server_.createParameter(constants::hold_duration_parameter_name);
  hold_duration_parameter.setRange(constants::duration_min,constants::duration_max);
  hold_duration_parameter.setUnits(constants::duration_units_name);

  ModularDevice::Parameter& pulse_wave_index_parameter = modular_server_.createParameter(constants::pulse_wave_index_parameter_name);
  pulse_wave_index_parameter.setRange((int)0,(constants::INDEXED_PULSES_COUNT_MAX-1));

  // Methods
  ModularDevice::Method& set_channel_on_method = modular_server_.createMethod(constants::set_channel_on_method_name);
  set_channel_on_method.attachCallback(callbacks::setChannelOnCallback);
  set_channel_on_method.addParameter(channel_parameter);

  ModularDevice::Method& set_channel_off_method = modular_server_.createMethod(constants::set_channel_off_method_name);
  set_channel_off_method.attachCallback(callbacks::setChannelOffCallback);
  set_channel_off_method.addParameter(channel_parameter);

  ModularDevice::Method& set_channels_on_method = modular_server_.createMethod(constants::set_channels_on_method_name);
  set_channels_on_method.attachCallback(callbacks::setChannelsOnCallback);
  set_channels_on_method.addParameter(channels_parameter);

  ModularDevice::Method& set_channels_off_method = modular_server_.createMethod(constants::set_channels_off_method_name);
  set_channels_off_method.attachCallback(callbacks::setChannelsOffCallback);
  set_channels_off_method.addParameter(channels_parameter);

  ModularDevice::Method& toggle_channel_method = modular_server_.createMethod(constants::toggle_channel_method_name);
  toggle_channel_method.attachCallback(callbacks::toggleChannelCallback);
  toggle_channel_method.addParameter(channel_parameter);

  ModularDevice::Method& toggle_channels_method = modular_server_.createMethod(constants::toggle_channels_method_name);
  toggle_channels_method.attachCallback(callbacks::toggleChannelsCallback);
  toggle_channels_method.addParameter(channels_parameter);

  ModularDevice::Method& toggle_all_channels_method = modular_server_.createMethod(constants::toggle_all_channels_method_name);
  toggle_all_channels_method.attachCallback(callbacks::toggleAllChannelsCallback);

  ModularDevice::Method& set_all_channels_on_method = modular_server_.createMethod(constants::set_all_channels_on_method_name);
  set_all_channels_on_method.attachCallback(callbacks::setAllChannelsOnCallback);

  ModularDevice::Method& set_all_channels_off_method = modular_server_.createMethod(constants::set_all_channels_off_method_name);
  set_all_channels_off_method.attachCallback(callbacks::setAllChannelsOffCallback);

  ModularDevice::Method& set_channel_on_all_others_off_method = modular_server_.createMethod(constants::set_channel_on_all_others_off_method_name);
  set_channel_on_all_others_off_method.attachCallback(callbacks::setChannelOnAllOthersOffCallback);
  set_channel_on_all_others_off_method.addParameter(channel_parameter);

  ModularDevice::Method& set_channel_off_all_others_on_method = modular_server_.createMethod(constants::set_channel_off_all_others_on_method_name);
  set_channel_off_all_others_on_method.attachCallback(callbacks::setChannelOffAllOthersOnCallback);
  set_channel_off_all_others_on_method.addParameter(channel_parameter);

  ModularDevice::Method& set_channels_on_all_others_off_method = modular_server_.createMethod(constants::set_channels_on_all_others_off_method_name);
  set_channels_on_all_others_off_method.attachCallback(callbacks::setChannelsOnAllOthersOffCallback);
  set_channels_on_all_others_off_method.addParameter(channels_parameter);

  ModularDevice::Method& set_channels_off_all_others_on_method = modular_server_.createMethod(constants::set_channels_off_all_others_on_method_name);
  set_channels_off_all_others_on_method.attachCallback(callbacks::setChannelsOffAllOthersOnCallback);
  set_channels_off_all_others_on_method.addParameter(channels_parameter);

  ModularDevice::Method& get_channels_on_method = modular_server_.createMethod(constants::get_channels_on_method_name);
  get_channels_on_method.attachCallback(callbacks::getChannelsOnCallback);

  ModularDevice::Method& get_channels_off_method = modular_server_.createMethod(constants::get_channels_off_method_name);
  get_channels_off_method.attachCallback(callbacks::getChannelsOffCallback);

  ModularDevice::Method& get_channel_count_method = modular_server_.createMethod(constants::get_channel_count_method_name);
  get_channel_count_method.attachCallback(callbacks::getChannelCountCallback);

  ModularDevice::Method& save_state_method = modular_server_.createMethod(constants::save_state_method_name);
  save_state_method.attachCallback(callbacks::saveStateCallback);
  save_state_method.addParameter(state_parameter);

  ModularDevice::Method& recall_state_method = modular_server_.createMethod(constants::recall_state_method_name);
  recall_state_method.attachCallback(callbacks::recallStateCallback);
  recall_state_method.addParameter(state_parameter);

  ModularDevice::Method& get_saved_states_method = modular_server_.createMethod(constants::get_saved_states_method_name);
  get_saved_states_method.attachCallback(callbacks::getSavedStatesCallback);

  ModularDevice::Method& add_pulse_centered_method = modular_server_.createMethod(constants::add_pulse_centered_method_name);
  add_pulse_centered_method.attachCallback(callbacks::addPulseCenteredCallback);
  add_pulse_centered_method.addParameter(channels_parameter);
  add_pulse_centered_method.addParameter(delay_parameter);
  add_pulse_centered_method.addParameter(on_duration_parameter);

  ModularDevice::Method& add_pwm_period_on_duration_method = modular_server_.createMethod(constants::add_pwm_period_on_duration_method_name);
  add_pwm_period_on_duration_method.attachCallback(callbacks::addPwmPeriodOnDurationCallback);
  add_pwm_period_on_duration_method.addParameter(channels_parameter);
  add_pwm_period_on_duration_method.addParameter(delay_parameter);
  add_pwm_period_on_duration_method.addParameter(period_parameter);
  add_pwm_period_on_duration_method.addParameter(on_duration_parameter);
  add_pwm_period_on_duration_method.addParameter(count_parameter);

  ModularDevice::Method& add_pwm_frequency_duty_cycle_method = modular_server_.createMethod(constants::add_pwm_frequency_duty_cycle_method_name);
  add_pwm_frequency_duty_cycle_method.attachCallback(callbacks::addPwmFrequencyDutyCycleCallback);
  add_pwm_frequency_duty_cycle_method.addParameter(channels_parameter);
  add_pwm_frequency_duty_cycle_method.addParameter(delay_parameter);
  add_pwm_frequency_duty_cycle_method.addParameter(frequency_parameter);
  add_pwm_frequency_duty_cycle_method.addParameter(duty_cycle_parameter);
  add_pwm_frequency_duty_cycle_method.addParameter(pwm_duration_parameter);

  ModularDevice::Method& add_spike_and_hold_method = modular_server_.createMethod(constants::add_spike_and_hold_method_name);
  add_spike_and_hold_method.attachCallback(callbacks::addSpikeAndHoldCallback);
  add_spike_and_hold_method.addParameter(channels_parameter);
  add_spike_and_hold_method.addParameter(delay_parameter);
  add_spike_and_hold_method.addParameter(spike_duty_cycle_parameter);
  add_spike_and_hold_method.addParameter(spike_duration_parameter);
  add_spike_and_hold_method.addParameter(hold_duty_cycle_parameter);
  add_spike_and_hold_method.addParameter(hold_duration_parameter);

  ModularDevice::Method& stop_all_pulses_method = modular_server_.createMethod(constants::stop_all_pulses_method_name);
  stop_all_pulses_method.attachCallback(callbacks::stopAllPulsesCallback);

  ModularDevice::Method& start_pwm_period_on_duration_method = modular_server_.createMethod(constants::start_pwm_period_on_duration_method_name);
  start_pwm_period_on_duration_method.attachCallback(callbacks::startPwmPeriodOnDurationCallback);
  start_pwm_period_on_duration_method.addParameter(channels_parameter);
  start_pwm_period_on_duration_method.addParameter(delay_parameter);
  start_pwm_period_on_duration_method.addParameter(period_parameter);
  start_pwm_period_on_duration_method.addParameter(on_duration_parameter);

  ModularDevice::Method& start_pwm_frequency_duty_cycle_method = modular_server_.createMethod(constants::start_pwm_frequency_duty_cycle_method_name);
  start_pwm_frequency_duty_cycle_method.attachCallback(callbacks::startPwmFrequencyDutyCycleCallback);
  start_pwm_frequency_duty_cycle_method.addParameter(channels_parameter);
  start_pwm_frequency_duty_cycle_method.addParameter(delay_parameter);
  start_pwm_frequency_duty_cycle_method.addParameter(frequency_parameter);
  start_pwm_frequency_duty_cycle_method.addParameter(duty_cycle_parameter);

  ModularDevice::Method& start_spike_and_hold_method = modular_server_.createMethod(constants::start_spike_and_hold_method_name);
  start_spike_and_hold_method.attachCallback(callbacks::startSpikeAndHoldCallback);
  start_spike_and_hold_method.addParameter(channels_parameter);
  start_spike_and_hold_method.addParameter(delay_parameter);
  start_spike_and_hold_method.addParameter(spike_duty_cycle_parameter);
  start_spike_and_hold_method.addParameter(spike_duration_parameter);
  start_spike_and_hold_method.addParameter(hold_duty_cycle_parameter);

  ModularDevice::Method& stop_pulse_wave_method = modular_server_.createMethod(constants::stop_pulse_wave_method_name);
  stop_pulse_wave_method.attachCallback(callbacks::stopPulseWaveCallback);
  stop_pulse_wave_method.addParameter(pulse_wave_index_parameter);

  // Setup Streams
  Serial.begin(constants::baudrate);

  // Start Modular Device Server
  modular_server_.startServer();
}

void Controller::update()
{
  modular_server_.handleServerRequests();
}

ModularDevice::ModularServer& Controller::getModularServer()
{
  return modular_server_;
}

void Controller::saveState(int state)
{
  if (state >= constants::STATE_COUNT)
  {
    return;
  }
  uint32_t channels = getChannelsOn();
  states_array_[state] = channels;
  modular_server_.setSavedVariableValue(constants::states_name,states_array_,state);
}

void Controller::recallState(int state)
{
  if (state >= constants::STATE_COUNT)
  {
    return;
  }
  modular_server_.getSavedVariableValue(constants::states_name,states_array_,state);
  uint32_t channels = states_array_[state];
  setChannels(channels);
}

void Controller::getStatesArray(uint32_t states_array[])
{
  for (int state=0; state<constants::STATE_COUNT; state++)
  {
    modular_server_.getSavedVariableValue(constants::states_name,states_array,state);
  }
}

Controller controller;
