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
// Callbacks must be non-blocking (avoid 'delay')
//
// modular_server.getParameterValue must be cast to either:
// const char*
// long
// double
// bool
// ArduinoJson::JsonArray&
// ArduinoJson::JsonObject&
//
// For more info read about ArduinoJson parsing https://github.com/janelia-arduino/ArduinoJson
//
// modular_server.getSavedVariableValue type must match the saved variable default type
// modular_server.setSavedVariableValue type must match the saved variable default type

ModularDevice::ModularServer& modular_server = controller.getModularServer();

IndexedContainer<uint32_t,constants::INDEXED_CHANNELS_COUNT_MAX> indexed_channels;
IndexedContainer<PulseInfo,constants::INDEXED_PULSES_COUNT_MAX> indexed_pulses;

void setChannelOnCallback()
{
  long channel = modular_server.getParameterValue(constants::channel_parameter_name);
  controller.setChannelOn(channel);
}

void setChannelOffCallback()
{
  long channel = modular_server.getParameterValue(constants::channel_parameter_name);
  controller.setChannelOff(channel);
}

void setChannelsOnCallback()
{
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  controller.setChannelsOn(channels);
}

void setChannelsOffCallback()
{
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  controller.setChannelsOff(channels);
}

void toggleChannelCallback()
{
  long channel = modular_server.getParameterValue(constants::channel_parameter_name);
  controller.toggleChannel(channel);
}

void toggleChannelsCallback()
{
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  controller.toggleChannels(channels);
}

void toggleAllChannelsCallback()
{
  controller.toggleAllChannels();
}

void setAllChannelsOnCallback()
{
  EventController::event_controller.removeAllEvents();
  controller.setAllChannelsOn();
}

void setAllChannelsOffCallback()
{
  EventController::event_controller.removeAllEvents();
  controller.setAllChannelsOff();
}

void setChannelOnAllOthersOffCallback()
{
  long channel = modular_server.getParameterValue(constants::channel_parameter_name);
  EventController::event_controller.removeAllEvents();
  controller.setChannelOnAllOthersOff(channel);
}

void setChannelOffAllOthersOnCallback()
{
  long channel = modular_server.getParameterValue(constants::channel_parameter_name);
  EventController::event_controller.removeAllEvents();
  controller.setChannelOffAllOthersOn(channel);
}

void setChannelsOnAllOthersOffCallback()
{
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  EventController::event_controller.removeAllEvents();
  controller.setChannelsOnAllOthersOff(channels);
}

void setChannelsOffAllOthersOnCallback()
{
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  EventController::event_controller.removeAllEvents();
  controller.setChannelsOffAllOthersOn(channels);
}

void getChannelsOnCallback()
{
  uint32_t channels_on = controller.getChannelsOn();
  uint32_t bit = 1;
  modular_server.writeResultKeyToResponse();
  modular_server.beginResponseArray();
  for (int channel=0; channel<constants::channel_count; channel++)
  {
    if (channels_on & (bit << channel))
    {
      modular_server.writeToResponse(channel);
    }
  }
  modular_server.endResponseArray();
}

void getChannelsOffCallback()
{
  uint32_t channels_on = controller.getChannelsOn();
  uint32_t channels_off = ~channels_on;
  uint32_t bit = 1;
  modular_server.writeResultKeyToResponse();
  modular_server.beginResponseArray();
  for (int channel=0; channel<constants::channel_count; channel++)
  {
    if (channels_off & (bit << channel))
    {
      modular_server.writeToResponse(channel);
    }
  }
  modular_server.endResponseArray();
}

void getChannelCountCallback()
{
  int channel_count = controller.getChannelCount();
  modular_server.writeResultToResponse(channel_count);
}

void saveStateCallback()
{
  long state = modular_server.getParameterValue(constants::state_parameter_name);
  controller.saveState(state);
}

void recallStateCallback()
{
  long state = modular_server.getParameterValue(constants::state_parameter_name);
  controller.recallState(state);
}

void getSavedStatesCallback()
{
  uint32_t states_array[constants::STATE_COUNT];
  controller.getStatesArray(states_array);
  uint32_t bit = 1;
  modular_server.writeResultKeyToResponse();
  modular_server.beginResponseArray();
  for (int state=0; state<constants::STATE_COUNT; state++)
  {
    modular_server.beginResponseArray();
    for (int channel=constants::channel_min; channel<=constants::channel_max; channel++)
    {
      if ((bit<<channel) & states_array[state])
      {
        modular_server.writeToResponse("on");
      }
      else
      {
        modular_server.writeToResponse("off");
      }
    }
    modular_server.endResponseArray();
  }
  modular_server.endResponseArray();
}

void addPulseCenteredCallback()
{
  if (indexed_channels.full())
  {
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  long on_duration = modular_server.getParameterValue(constants::on_duration_parameter_name);
  long start_delay = delay - on_duration/2;
  if (start_delay < 0)
  {
    start_delay = 0;
  }
  EventController::EventId on_event_id = EventController::event_controller.addEventUsingDelay(setChannelsOnEventCallback,
                                                                                              start_delay,
                                                                                              index);
  EventController::event_controller.addEventUsingOffset(setChannelsOffEventCallback,
                                                        on_event_id,
                                                        on_duration,
                                                        index,
                                                        NULL,
                                                        removeIndexedChannelCallback);
}

void addPwmPeriodOnDurationCallback()
{
  if (indexed_channels.full())
  {
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  long period = modular_server.getParameterValue(constants::period_parameter_name);
  long on_duration = modular_server.getParameterValue(constants::on_duration_parameter_name);
  long count = modular_server.getParameterValue(constants::count_parameter_name);
  EventController::event_controller.addPwmUsingDelayPeriodOnDuration(setChannelsOnEventCallback,
                                                                     setChannelsOffEventCallback,
                                                                     delay,
                                                                     period,
                                                                     on_duration,
                                                                     count,
                                                                     index,
                                                                     NULL,
                                                                     removeIndexedChannelCallback);
}

void addPwmFrequencyDutyCycleCallback()
{
  if (indexed_channels.full())
  {
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  double frequency = modular_server.getParameterValue(constants::frequency_parameter_name);
  long duty_cycle = modular_server.getParameterValue(constants::duty_cycle_parameter_name);
  long pwm_duration = modular_server.getParameterValue(constants::pwm_duration_parameter_name);
  uint32_t period = 1000/frequency;
  period = max(period,2);
  uint32_t on_duration = (period*duty_cycle)/100;
  on_duration = constrain(on_duration,1,period-1);
  uint32_t count = pwm_duration/period;
  EventController::event_controller.addPwmUsingDelayPeriodOnDuration(setChannelsOnEventCallback,
                                                                     setChannelsOffEventCallback,
                                                                     delay,
                                                                     period,
                                                                     on_duration,
                                                                     count,
                                                                     index,
                                                                     NULL,
                                                                     removeIndexedChannelCallback);
}

void addSpikeAndHoldCallback()
{
  if (indexed_channels.full())
  {
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  long spike_duty_cycle = modular_server.getParameterValue(constants::spike_duty_cycle_parameter_name);
  long spike_duration = modular_server.getParameterValue(constants::spike_duration_parameter_name);
  spike_duration = max(spike_duration,2);
  long hold_duty_cycle = modular_server.getParameterValue(constants::hold_duty_cycle_parameter_name);
  long hold_duration = modular_server.getParameterValue(constants::hold_duration_parameter_name);
  hold_duration = max(hold_duration,2);

  spikeAndHold(index,delay,spike_duty_cycle,spike_duration,hold_duty_cycle,hold_duration);
}

void stopAllPulsesCallback()
{
  EventController::event_controller.removeAllEvents();
  for (int i=0; i<indexed_channels.max_size(); ++i)
  {
    if (indexed_channels.indexHasValue(i))
    {
      setChannelsOffEventCallback(i);
    }
  }
  indexed_channels.clear();
}

void startPwmPeriodOnDurationCallback()
{
  if (indexed_channels.full() || indexed_pulses.full())
  {
    modular_server.writeResultToResponse(-1);
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  long period = modular_server.getParameterValue(constants::period_parameter_name);
  long on_duration = modular_server.getParameterValue(constants::on_duration_parameter_name);
  PulseInfo pulse_info;
  EventController::EventIdPair event_id_pair =
    EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(setChannelsOnEventCallback,
                                                                               setChannelsOffEventCallback,
                                                                               delay,
                                                                               period,
                                                                               on_duration,
                                                                               index);
  pulse_info.event_id_pair = event_id_pair;
  pulse_info.channel_index = index;
  int pulse_wave_index = indexed_pulses.add(pulse_info);
  modular_server.writeResultToResponse(pulse_wave_index);
}

void startPwmFrequencyDutyCycleCallback()
{
  if (indexed_channels.full() || indexed_pulses.full())
  {
    modular_server.writeResultToResponse(-1);
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  double frequency = modular_server.getParameterValue(constants::frequency_parameter_name);
  long duty_cycle = modular_server.getParameterValue(constants::duty_cycle_parameter_name);
  long pwm_duration = modular_server.getParameterValue(constants::pwm_duration_parameter_name);
  uint32_t period = 1000/frequency;
  period = max(period,2);
  uint32_t on_duration = (period*duty_cycle)/100;
  on_duration = constrain(on_duration,1,period-1);
  PulseInfo pulse_info;
  EventController::EventIdPair event_id_pair =
    EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(setChannelsOnEventCallback,
                                                                               setChannelsOffEventCallback,
                                                                               delay,
                                                                               period,
                                                                               on_duration,
                                                                               index);
  pulse_info.event_id_pair = event_id_pair;
  pulse_info.channel_index = index;
  int pulse_wave_index = indexed_pulses.add(pulse_info);
  modular_server.writeResultToResponse(pulse_wave_index);
}

void startSpikeAndHoldCallback()
{
  if (indexed_channels.full() || indexed_pulses.full())
  {
    modular_server.writeResultToResponse(-1);
    return;
  }
  ArduinoJson::JsonArray& channels_array = modular_server.getParameterValue(constants::channels_parameter_name);
  uint32_t channels = arrayToChannels(channels_array);
  int index = indexed_channels.add(channels);
  long delay = modular_server.getParameterValue(constants::delay_parameter_name);
  long spike_duty_cycle = modular_server.getParameterValue(constants::spike_duty_cycle_parameter_name);
  long spike_duration = modular_server.getParameterValue(constants::spike_duration_parameter_name);
  spike_duration = max(spike_duration,2);
  long hold_duty_cycle = modular_server.getParameterValue(constants::hold_duty_cycle_parameter_name);
  long hold_duration = -1;

  PulseInfo pulse_info = spikeAndHold(index,delay,spike_duty_cycle,spike_duration,hold_duty_cycle,hold_duration);

  int pulse_wave_index = indexed_pulses.add(pulse_info);
  modular_server.writeResultToResponse(pulse_wave_index);
}

void stopPulseWaveCallback()
{
  long pulse_wave_index = modular_server.getParameterValue(constants::pulse_wave_index_parameter_name);
  PulseInfo &pulse_info = indexed_pulses[pulse_wave_index];
  EventController::event_controller.removeEventPair(pulse_info.event_id_pair);
  setChannelsOffEventCallback(pulse_info.channel_index);
  indexed_channels.remove(pulse_info.channel_index);
  indexed_pulses.remove(pulse_wave_index);
}

uint32_t arrayToChannels(ArduinoJson::JsonArray& channels_array)
{
  uint32_t channels = 0;
  uint32_t bit = 1;
  for (ArduinoJson::JsonArray::iterator channels_it=channels_array.begin();
       channels_it != channels_array.end();
       ++channels_it)
  {
    long channel = *channels_it;
    channels |= bit << channel;
  }
  return channels;
}

PulseInfo spikeAndHold(int index,
                       uint32_t delay,
                       uint32_t spike_duty_cycle,
                       uint32_t spike_duration,
                       uint32_t hold_duty_cycle,
                       long hold_duration)
{
  uint32_t on_duration = 1;
  uint32_t off_duration = 1;
  uint32_t period = 0;
  uint32_t count = 0;
  if (spike_duty_cycle <= 50)
  {
    period = (100*on_duration)/spike_duty_cycle;
    period = constrain(period,2,spike_duration);
  }
  else
  {
    off_duration = 1;
    period = (100*off_duration)/(100-spike_duty_cycle);
    period = constrain(period,2,spike_duration);
    on_duration = period - off_duration;
  }
  count = spike_duration/period;
  EventController::EventIdPair pwm_event_id_pair =
    EventController::event_controller.addPwmUsingDelayPeriodOnDuration(setChannelsOnEventCallback,
                                                                       setChannelsOffEventCallback,
                                                                       delay,
                                                                       period,
                                                                       on_duration,
                                                                       count,
                                                                       index);

  on_duration = 1;
  if (hold_duty_cycle <= 50)
  {
    period = (100*on_duration)/hold_duty_cycle;
    period = constrain(period,2,hold_duration);
  }
  else
  {
    off_duration = 1;
    period = (100*off_duration)/(100-hold_duty_cycle);
    period = constrain(period,2,hold_duration);
    on_duration = period - off_duration;
  }
  PulseInfo pulse_info;
  EventController::EventIdPair event_id_pair;
  if (hold_duration > 0)
  {
    count = hold_duration/period;
    event_id_pair =
      EventController::event_controller.addPwmUsingOffsetPeriodOnDuration(setChannelsOnEventCallback,
                                                                          setChannelsOffEventCallback,
                                                                          pwm_event_id_pair.event_id_0,
                                                                          spike_duration,
                                                                          period,
                                                                          on_duration,
                                                                          count,
                                                                          index,
                                                                          NULL,
                                                                          removeIndexedChannelCallback);
  }
  else
  {
    event_id_pair =
      EventController::event_controller.addInfinitePwmUsingOffsetPeriodOnDuration(setChannelsOnEventCallback,
                                                                                  setChannelsOffEventCallback,
                                                                                  pwm_event_id_pair.event_id_0,
                                                                                  spike_duration,
                                                                                  period,
                                                                                  on_duration,
                                                                                  index);
  }
  pulse_info.event_id_pair = event_id_pair;
  pulse_info.channel_index = index;
  return pulse_info;
}

// EventController Callbacks
void removeIndexedChannelCallback(int index)
{
  indexed_channels.remove(index);
}

void setChannelsOnEventCallback(int index)
{
  uint32_t channels = indexed_channels[index];
  controller.setChannelsOn(channels);
}

void setChannelsOffEventCallback(int index)
{
  uint32_t channels = indexed_channels[index];
  controller.setChannelsOff(channels);
}

}
