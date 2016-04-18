# -*- coding: utf-8 -*-
from __future__ import print_function, division
import serial
import time
import atexit
import yaml
import sys
import argparse
import datetime

from serial_device2 import SerialDevice, SerialDevices, find_serial_device_ports, WriteFrequencyError

DEBUG = True
BAUDRATE = 9600


class SleepAssay(object):
    '''
    '''
    _TIMEOUT = 0.05
    _WRITE_WRITE_DELAY = 0.05
    _RESET_DELAY = 2.0
    _RELAY_COUNT = 8
    _CAMERA_TRIGGER_DUTY_CYCLE = 50
    _BOARD_INDICATOR_LIGHT_FREQUENCY = 2
    _BOARD_INDICATOR_LIGHT_DUTY_CYCLE = 50
    _MILLISECONDS_PER_SECOND = 1000
    _SECONDS_PER_MINUTE = 60
    _MINUTES_PER_HOUR = 60
    _HOURS_PER_DAY = 24
    _MILLISECONDS_PER_HOUR = _MILLISECONDS_PER_SECOND*_SECONDS_PER_MINUTE*_MINUTES_PER_HOUR
    _MILLISECONDS_PER_DAY = _MILLISECONDS_PER_HOUR*_HOURS_PER_DAY

    _METHOD_ID_START_PWM = 0
    _METHOD_ID_START_PWM_PATTERN = 1
    _METHOD_ID_STOP_ALL_PULSES = 2

    def __init__(self,config_file_path,*args,**kwargs):
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            # kwargs.update({'debug': DEBUG})
            self.debug = DEBUG
        if 'baudrate' not in kwargs:
            kwargs.update({'baudrate': BAUDRATE})
        elif (kwargs['baudrate'] is None) or (str(kwargs['baudrate']).lower() == 'default'):
            kwargs.update({'baudrate': BAUDRATE})
        if 'timeout' not in kwargs:
            kwargs.update({'timeout': self._TIMEOUT})
        if 'write_write_delay' not in kwargs:
            kwargs.update({'write_write_delay': self._WRITE_WRITE_DELAY})
        with open(config_file_path,'r') as config_stream:
            self._config = yaml.load(config_stream)
        if ('relay_board_serial_port' not in self._config):
            raise RuntimeError('Must specify serial port in config file!')
        else:
            kwargs['port'] = self._config['relay_board_serial_port']

        t_start = time.time()
        self._serial_device = SerialDevice(*args,**kwargs)
        atexit.register(self._exit_sleep_assay)
        time.sleep(self._RESET_DELAY)
        t_end = time.time()
        self._debug_print('Initialization time =', (t_end - t_start))

    def _debug_print(self, *args):
        if self.debug:
            print(*args)

    def _exit_sleep_assay(self):
        self.stop()

    def _args_to_request(self,*args):
        request = ['[', ','.join(map(str,args)), ']']
        request = ''.join(request)
        request = request + '\n';
        return request

    def _send_request(self,*args):

        '''Sends request to device over serial port and
        returns number of bytes written'''

        request = self._args_to_request(*args)
        self._debug_print('request', request)
        bytes_written = self._serial_device.write_check_freq(request,
                                                             delay_write=True)
        return bytes_written

    def _close(self):
        '''
        Close the device serial port.
        '''
        self._serial_device.close()

    def _get_port(self):
        return self._serial_device.port

    def _start_pwm_period_on_duration(self,
                                      relay,
                                      period,
                                      on_duration,
                                      delay):
        '''
        '''
        if relay < 0:
            relay = 0
        elif relay > (self._RELAY_COUNT - 1):
            relay = self._RELAY_COUNT
        period = int(period)
        on_duration = int(on_duration)
        delay = int(delay)
        self._send_request(self._METHOD_ID_START_PWM,
                           relay,
                           period,
                           on_duration,
                           delay)

    def _start_pwm_pattern(self,
                           relay,
                           pwm_period,
                           pwm_on_duration,
                           pattern_period,
                           pattern_on_duration,
                           delay):
        '''
        '''
        if relay < 0:
            relay = 0
        elif relay > (self._RELAY_COUNT - 1):
            relay = self._RELAY_COUNT
        pwm_period = int(pwm_period)
        pwm_on_duration = int(pwm_on_duration)
        pattern_period = int(pattern_period)
        pattern_on_duration = int(pattern_on_duration)
        delay = int(delay)
        self._send_request(self._METHOD_ID_START_PWM_PATTERN,
                           relay,
                           pwm_period,
                           pwm_on_duration,
                           pattern_period,
                           pattern_on_duration,
                           delay)

    def _start_pwm_frequency_duty_cycle(self,
                                        relay,
                                        frequency,
                                        duty_cycle,
                                        delay):
        '''
        '''
        period = 1000/frequency
        on_duration = (duty_cycle/100)*period
        self._start_pwm_period_on_duration(relay,period,on_duration,delay)

    def _stop_all_pulses(self):
        '''
        '''
        self._send_request(self._METHOD_ID_STOP_ALL_PULSES)

    def _start_to_delay(self,start):
        start_datetime = datetime.datetime(start['year'],
                                           start['month'],
                                           start['day'],
                                           start['hour'],
                                           start['minute'])
        now_datetime = datetime.datetime.now()
        delta = start_datetime - now_datetime
        delay = int(self._MILLISECONDS_PER_SECOND*delta.total_seconds())
        if delay < 0:
            delay = 0
        return delay

    def start_board_indicator_light_cycle(self,relay):
        self._debug_print('start_board_indicator_light_cycle:')
        self._BOARD_INDICATOR_LIGHT_FREQUENCY
        self._start_pwm_frequency_duty_cycle(relay,
                                             self._BOARD_INDICATOR_LIGHT_FREQUENCY,
                                             self._BOARD_INDICATOR_LIGHT_DUTY_CYCLE,
                                             delay=0)

    def start_camera_trigger(self,
                             relay,
                             frame_rate,
                             start):
        self._debug_print('start_camera_trigger:')
        self._debug_print('  relay = {0}'.format(relay))
        self._debug_print('  frame_rate = {0}'.format(frame_rate))
        self._debug_print('  start:')
        self._debug_print('    {0}-{1}-{2}-{3}:{4}'.format(start['year'],
                                                           start['month'],
                                                           start['day'],
                                                           start['hour'],
                                                           start['minute']))
        delay = self._start_to_delay(start)
        self._start_pwm_frequency_duty_cycle(relay,
                                             frame_rate,
                                             self._CAMERA_TRIGGER_DUTY_CYCLE,
                                             delay)

    def start_white_light_cycle(self,
                                relay,
                                pwm_on_duration_hours,
                                pwm_off_duration_hours,
                                pattern_on_duration_days,
                                pattern_off_duration_days,
                                start):
        self._debug_print('start_white_light_cycle:')
        self._debug_print('  relay = {0}'.format(relay))
        self._debug_print('  pwm_on_duration_hours = {0}'.format(pwm_on_duration_hours))
        self._debug_print('  pwm_off_duration_hours = {0}'.format(pwm_off_duration_hours))
        self._debug_print('  pattern_on_duration_days = {0}'.format(pattern_on_duration_days))
        self._debug_print('  pattern_off_duration_days = {0}'.format(pattern_off_duration_days))
        self._debug_print('  start:')
        self._debug_print('    {0}-{1}-{2}-{3}:{4}'.format(start['year'],
                                                           start['month'],
                                                           start['day'],
                                                           start['hour'],
                                                           start['minute']))
        pwm_period = (pwm_on_duration_hours + pwm_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pwm_on_duration = pwm_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pattern_period = (pattern_on_duration_days + pattern_off_duration_days)*self._MILLISECONDS_PER_DAY
        pattern_on_duration = pattern_on_duration_days*self._MILLISECONDS_PER_DAY
        delay = self._start_to_delay(start)
        self._start_pwm_pattern(relay,
                                pwm_period,
                                pwm_on_duration,
                                pattern_period,
                                pattern_on_duration,
                                delay)

    def start_red_light_cycle(self,
                              relay,
                              pwm_frequency,
                              pwm_duty_cycle,
                              pattern_on_duration_hours,
                              pattern_off_duration_hours,
                              start):
        self._debug_print('start_white_light_cycle:')
        self._debug_print('  relay = {0}'.format(relay))
        self._debug_print('  pwm_frequency = {0}'.format(pwm_frequency))
        self._debug_print('  pwm_duty_cycle = {0}'.format(pwm_duty_cycle))
        self._debug_print('  pattern_on_duration_hours = {0}'.format(pattern_on_duration_hours))
        self._debug_print('  pattern_off_duration_hours = {0}'.format(pattern_off_duration_hours))
        self._debug_print('  start:')
        self._debug_print('    {0}-{1}-{2}-{3}:{4}'.format(start['year'],
                                                           start['month'],
                                                           start['day'],
                                                           start['hour'],
                                                           start['minute']))
        pwm_period = 1000/pwm_frequency
        pwm_on_duration = (pwm_duty_cycle/100)*pwm_period
        pattern_period = (pattern_on_duration_hours + pattern_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pattern_on_duration = pattern_on_duration_hours*self._MILLISECONDS_PER_HOUR
        delay = self._start_to_delay(start)
        self._start_pwm_pattern(relay,
                                pwm_period,
                                pwm_on_duration,
                                pattern_period,
                                pattern_on_duration,
                                delay)

    def stop(self):
        self._stop_all_pulses()

    def start(self):
        self.start_board_indicator_light_cycle(self._config['board_indicator_light']['relay'])
        self.start_camera_trigger(self._config['camera']['relay'],
                                  self._config['camera']['frame_rate_hz'],
                                  self._config['camera']['start'])
        self.start_white_light_cycle(self._config['white_light']['relay'],
                                     self._config['white_light']['pwm_on_duration_hours'],
                                     self._config['white_light']['pwm_off_duration_hours'],
                                     self._config['white_light']['pattern_on_duration_days'],
                                     self._config['white_light']['pattern_off_duration_days'],
                                     self._config['white_light']['start'])
        self.start_red_light_cycle(self._config['red_light']['relay'],
                                   self._config['red_light']['pwm_frequency_hz'],
                                   self._config['red_light']['pwm_duty_cycle_percent'],
                                   self._config['red_light']['pattern_on_duration_hours'],
                                   self._config['red_light']['pattern_off_duration_hours'],
                                   self._config['red_light']['start'])


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file_path", help="Path to yaml config file.")

    args = parser.parse_args()
    config_file_path = args.config_file_path
    print("Config File Path: {0}".format(config_file_path))

    sa = SleepAssay(config_file_path)
    sa.start()
    while(True):
        pass


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
