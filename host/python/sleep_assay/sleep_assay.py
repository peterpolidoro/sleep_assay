# -*- coding: utf-8 -*-
from __future__ import print_function, division
import serial
import time
import atexit
import yaml

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
    _MILLISECONDS_PER_SECOND = 1000
    _SECONDS_PER_MINUTE = 60
    _MINUTES_PER_HOUR = 60
    _HOURS_PER_DAY = 24
    _METHOD_ID_START_PWM = 0
    _METHOD_ID_START_PWM_PATTERN = 1
    _METHOD_ID_STOP_ALL_PULSES = 2

    def __init__(self,config_file_path,*args,**kwargs):
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            kwargs.update({'debug': DEBUG})
            self.debug = DEBUG
        if 'baudrate' not in kwargs:
            kwargs.update({'baudrate': BAUDRATE})
        elif (kwargs['baudrate'] is None) or (str(kwargs['baudrate']).lower() == 'default'):
            kwargs.update({'baudrate': BAUDRATE})
        if 'timeout' not in kwargs:
            kwargs.update({'timeout': self._TIMEOUT})
        if 'write_write_delay' not in kwargs:
            kwargs.update({'write_write_delay': self._WRITE_WRITE_DELAY})
        with open(self._config_file_path,'r') as config_stream:
            self._config = yaml.load(config_stream)
        if ('port' not in self._config):
            raise RuntimeError('Must specify serial port!')
        else:
            kwargs['port'] = self._config.port

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
        bytes_written = self._serial_device.write_check_freq(request,delay_write=True)
        return bytes_written

    def _close(self):
        '''
        Close the device serial port.
        '''
        self._serial_device.close()

    def _get_port(self):
        return self._serial_device.port

    def _start_pwm_period_on_duration(self,relay,period,on_duration):
        '''
        '''
        if relay < 0:
            relay = 0
        elif relay > (self._RELAY_COUNT - 1):
            relay = self._RELAY_COUNT
        period = int(period)
        on_duration = int(on_duration)
        self._send_request(self._METHOD_ID_START_PWM,relay,period,on_duration)

    def _start_pwm_pattern(self,relay,pwm_period,pwm_on_duration,pattern_period,pattern_on_duration):
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
        self._send_request(self._METHOD_ID_START_PWM_PATTERN,relay,pwm_period,pwm_on_duration,pattern_period,pattern_on_duration)

    def _start_pwm_frequency_duty_cycle(self,relay,frequency,duty_cycle):
        '''
        '''
        period = 1000/frequency
        on_duration = (duty_cycle/100)*period
        self._start_pwm_period_on_duration(relay,period,on_duration)

    def _stop_all_pulses(self):
        '''
        '''
        self._send_request(self._METHOD_ID_STOP_ALL_PULSES)

    def start_camera_trigger(self,relay,frame_rate):
        self._start_pwm_frequency_duty_cycle(relay,frame_rate,self._CAMERA_TRIGGER_DUTY_CYCLE)

    def start_white_light_cycle(self,relay,pwm_on_duration_hours,pwm_off_duration_hours,pattern_on_duration_days,pattern_off_duration_days):
        milliseconds_per_hour = self._MILLISECONDS_PER_SECOND*self._SECONDS_PER_MINUTE*self._MINUTES_PER_HOUR
        milliseconds_per_day = milliseconds_per_hour*self._HOURS_PER_DAY
        pwm_period = (pwm_on_duration_hours + pwm_off_duration_hours)*milliseconds_per_hour
        pwm_on_duration = pwm_on_duration_hours*milliseconds_per_hour
        pattern_period = (pattern_on_duration_days + pattern_off_duration_days)*milliseconds_per_day
        pattern_on_duration = pattern_on_duration_days*milliseconds_per_day
        self._start_pwm_pattern(relay,pwm_period,pwm_on_duration,pattern_period,pattern_on_duration)

    def start_red_light_cycle(self,relay,pwm_frequency,pwm_duty_cycle,pattern_on_duration_hours,pattern_off_duration_hours):
        milliseconds_per_hour = self._MILLISECONDS_PER_SECOND*self._SECONDS_PER_MINUTE*self._MINUTES_PER_HOUR
        pwm_period = 1000/pwm_frequency
        pwm_on_duration = (pwm_duty_cycle/100)*pwm_period
        pattern_period = (pattern_on_duration_hours + pattern_off_duration_hours)*milliseconds_per_hour
        pattern_on_duration = pattern_on_duration_hours*milliseconds_per_hour
        self._start_pwm_pattern(relay,pwm_period,pwm_on_duration,pattern_period,pattern_on_duration)

    def stop(self):
        self._stop_all_pulses()


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':

    debug = False
    dev = SleepAssay(debug=debug)
