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

SerialReceiver& g_serial_receiver = controller.getSerialReceiver();

IndexedContainer<PwmInfo,constants::INDEXED_PWMS_COUNT_MAX> g_indexed_pwms;

void startPwmCallback()
{
  int serial_receiver_position = 1;
  int relay = g_serial_receiver.readInt(serial_receiver_position++);
  int power = g_serial_receiver.readInt(serial_receiver_position++);
  if (power < constants::power_min)
  {
    power = constants::power_min;
  }
  else if (power > constants::power_max)
  {
    power = constants::power_max;
  }
  if (power < constants::power_max)
  {
    uint8_t relay_pin = constants::relay_pins[relay];
    bool relay_pin_is_high_freq = false;
    for (uint8_t r=0; r<constants::HIGH_FREQ_RELAY_COUNT; ++r)
    {
      if (relay_pin == constants::high_freq_relay_pins[r])
      {
        relay_pin_is_high_freq = true;
        break;
      }
    }
    if (!relay_pin_is_high_freq)
    {
      power = constants::power_max;
    }
  }

  long delay = g_serial_receiver.readLong(serial_receiver_position++);
  int pwm_level_count = g_serial_receiver.readInt(serial_receiver_position++);
  if (pwm_level_count < constants::PWM_LEVEL_COUNT_MIN)
  {
    pwm_level_count = constants::PWM_LEVEL_COUNT_MIN;
  }
  else if (pwm_level_count > constants::PWM_LEVEL_COUNT_MAX)
  {
    pwm_level_count = constants::PWM_LEVEL_COUNT_MAX;
  }
  if ((g_indexed_pwms.max_size() - g_indexed_pwms.size()) < pwm_level_count)
  {
    return;
  }

  long period = g_serial_receiver.readLong(serial_receiver_position++);
  long on_duration = g_serial_receiver.readLong(serial_receiver_position++);

  PwmInfo pwm_info;
  pwm_info.relay = relay;
  pwm_info.power = power;
  pwm_info.level = 0;
  pwm_info.child_index = -1;
  pwm_info.period = period;
  pwm_info.on_duration = on_duration;
  int index = g_indexed_pwms.add(pwm_info);

  for (int pwm_level=1; pwm_level < pwm_level_count; ++pwm_level)
  {
    pwm_info.relay = relay;
    pwm_info.power = power;
    pwm_info.level = pwm_level;
    pwm_info.child_index = index;
    period = g_serial_receiver.readLong(serial_receiver_position++);
    on_duration = g_serial_receiver.readLong(serial_receiver_position++);
    pwm_info.period = period;
    pwm_info.on_duration = on_duration;
    index = g_indexed_pwms.add(pwm_info);
  }

  EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(startPowerPwmEventCallback,
                                                                             stopPwmEventCallback,
                                                                             delay,
                                                                             pwm_info.period,
                                                                             pwm_info.on_duration,
                                                                             index);
}

void stopAllPwmCallback()
{
  EventController::event_controller.removeAllEvents();
  g_indexed_pwms.clear();
  controller.openAllRelays();
  controller.setAllPwmStatusStopped();
}

void getPowerCallback()
{
  Serial << "[";
  int power;
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    if (relay > 0)
    {
      Serial << ",";
    }
    power = controller.getPower(relay);
    Serial << power;
  }
  Serial << "]\n";
}

void getPwmStatusCallback()
{
  Serial << "[";
  constants::PwmStatus pwm_status;
  for (uint8_t relay=0; relay<constants::RELAY_COUNT; ++relay)
  {
    if (relay > 0)
    {
      Serial << ",";
    }
    Serial << "[";
    for (uint8_t level=0; level<constants::PWM_LEVEL_COUNT_MAX; ++level)
    {
      if (level > 0)
      {
        Serial << ",";
      }
      pwm_status = controller.getPwmStatus(relay,level);
      Serial << pwm_status;
    }
    Serial << "]";
  }
  Serial << "]\n";
}

// EventController Callbacks
void startPowerPwmEventCallback(int index)
{
  int relay = g_indexed_pwms[index].relay;
  int level = g_indexed_pwms[index].level;
  controller.setPwmStatusRunning(relay,level);
  int child_index = g_indexed_pwms[index].child_index;
  if (child_index < 0)
  {
    int power = g_indexed_pwms[index].power;
    controller.setRelayPower(relay,power);
  }
  else
  {
    long period = g_indexed_pwms[child_index].period;
    long on_duration = g_indexed_pwms[child_index].on_duration;
    int relay = g_indexed_pwms[child_index].relay;
    g_indexed_pwms[child_index].event_id_pair =
      EventController::event_controller.addInfinitePwmUsingDelayPeriodOnDuration(startPowerPwmEventCallback,
                                                                                 stopPwmEventCallback,
                                                                                 0,
                                                                                 period,
                                                                                 on_duration,
                                                                                 child_index);
  }
}

void stopPwmEventCallback(int index)
{
  int relay = g_indexed_pwms[index].relay;
  controller.openRelay(relay);
  int level = g_indexed_pwms[index].level;
  controller.setPwmStatusStopped(relay,level);
  int child_index = g_indexed_pwms[index].child_index;
  if (child_index >= 0)
  {
    EventController::event_controller.removeEventPair(g_indexed_pwms[child_index].event_id_pair);
    stopPwmEventCallback(child_index);
  }
}

}
