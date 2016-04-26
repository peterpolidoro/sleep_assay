# -*- coding: utf-8 -*-
from __future__ import print_function, division
import serial
import time
import atexit
import yaml
import sys
import argparse
import datetime
import platform
import json
import csv
import os

from serial_device2 import SerialDevice, SerialDevices, find_serial_device_ports, WriteFrequencyError

DEBUG = False
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
    _METHOD_ID_START_PWM_PATTERN_POWER = 2
    _METHOD_ID_STOP_ALL_PULSES = 3
    _METHOD_ID_GET_POWER = 4
    _METHOD_ID_GET_PWM_STATUS = 5

    _PWM_STOPPED = 0
    _PWM_RUNNING = 1

    def __init__(self,config_file_path,*args,**kwargs):
        self._config_file_path = os.path.abspath(config_file_path)
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
        os_type = platform.system()
        if os_type == 'Linux':
            if ('relay_board_serial_port_linux' not in self._config):
                raise RuntimeError('Must specify linux serial port in config file!')
            else:
                kwargs['port'] = self._config['relay_board_serial_port_linux']
        elif os_type == 'Windows':
            if ('relay_board_serial_port_windows' not in self._config):
                raise RuntimeError('Must specify windows serial port in config file!')
            else:
                kwargs['port'] = self._config['relay_board_serial_port_windows']
        elif os_type == 'Darwin':
            if ('relay_board_serial_port_osx' not in self._config):
                raise RuntimeError('Must specify osx serial port in config file!')
            else:
                kwargs['port'] = self._config['relay_board_serial_port']
        t_start = time.time()
        self._serial_device = SerialDevice(*args,**kwargs)
        atexit.register(self._exit_sleep_assay)
        time.sleep(self._RESET_DELAY)
        self._csv_file = None
        self._csv_writer = None
        self._header = ['row',
                        'video_frame',
                        'date_time',
                        'camera_trigger_on_off',
                        'white_light_power',
                        'red_light_on_off']
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

    def _send_request_get_result(self,*args):
        '''
        Sends request to server over serial port and
        returns response result
        '''
        request = self._args_to_request(*args)
        self._debug_print('request', request)
        response = self._serial_device.write_read(request,use_readline=True,check_write_freq=True)
        self._debug_print('response', response)
        result = json.loads(response)
        return result

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

    def _start_pwm_pattern_power(self,
                                 relay,
                                 pwm_period,
                                 pwm_on_duration,
                                 pattern_period,
                                 pattern_on_duration,
                                 delay,
                                 power):
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
        power = int(power)
        self._send_request(self._METHOD_ID_START_PWM_PATTERN_POWER,
                           relay,
                           pwm_period,
                           pwm_on_duration,
                           pattern_period,
                           pattern_on_duration,
                           delay,
                           power)

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

    def _get_power(self):
        '''
        '''
        result = self._send_request_get_result(self._METHOD_ID_GET_POWER)
        return result

    def _get_pwm_status(self):
        '''
        '''
        result = self._send_request_get_result(self._METHOD_ID_GET_PWM_STATUS)
        return result

    def _start_to_start_datetime(self,start):
        now_datetime = datetime.datetime.now()
        offset = datetime.timedelta(start['offset_days'])
        offset_datetime = now_datetime + offset
        start_datetime = datetime.datetime(offset_datetime.year,
                                           offset_datetime.month,
                                           offset_datetime.day,
                                           start['hour'],
                                           start['minute'])
        delta = start_datetime - now_datetime
        delay = int(self._MILLISECONDS_PER_SECOND*delta.total_seconds())
        if delay < 0:
            start_datetime = now_datetime
        print('  start:')
        print('    {0}-{1}-{2}-{3}-{4}'.format(start_datetime.year,
                                               start_datetime.month,
                                               start_datetime.day,
                                               start_datetime.hour,
                                               start_datetime.minute))
        return start_datetime

    def _start_datetime_to_delay(self,start_datetime):
        now_datetime = datetime.datetime.now()
        delta = start_datetime - now_datetime
        delay = int(self._MILLISECONDS_PER_SECOND*delta.total_seconds())
        if delay < 0:
            delay = 0
        return delay

    def _writerow(self,columns):
        if self._csv_writer is not None:
            utf8row = []
            for col in columns:
                utf8row.append(str(col).encode('utf8'))
            self._csv_writer.writerow(utf8row)

    def _get_date_str(self):
        today = datetime.date.today()
        date_str = "{year}-{month}-{day}".format(year=today.year,
                                                 month=today.month,
                                                 day=today.day)
        return date_str

    def _get_time_str(self):
        localtime = time.localtime()
        time_str = "{hour}-{min}-{sec}".format(hour=localtime.tm_hour,
                                               min=localtime.tm_min,
                                               sec=localtime.tm_sec)
        return time_str

    def _get_date_time_str(self):
        date_str = self._get_date_str()
        time_str = self._get_time_str()
        return date_str + '-' + time_str

    def start_board_indicator_light_cycle(self,relay):
        self._start_pwm_frequency_duty_cycle(relay,
                                             self._BOARD_INDICATOR_LIGHT_FREQUENCY,
                                             self._BOARD_INDICATOR_LIGHT_DUTY_CYCLE,
                                             delay=0)

    def start_camera_trigger(self,
                             relay,
                             frame_rate,
                             start):
        print('start_camera_trigger:')
        print('  relay = {0}'.format(relay))
        print('  frame_rate = {0}'.format(frame_rate))
        start_datetime = self._start_to_start_datetime(start)
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm_frequency_duty_cycle(relay,
                                             frame_rate,
                                             self._CAMERA_TRIGGER_DUTY_CYCLE,
                                             delay)
        return start_datetime

    def start_white_light_cycle(self,
                                relay,
                                pwm_on_duration_hours,
                                pwm_off_duration_hours,
                                pattern_on_duration_days,
                                pattern_off_duration_days,
                                power,
                                start):
        print('start_white_light_cycle:')
        print('  relay = {0}'.format(relay))
        print('  pwm_on_duration_hours = {0}'.format(pwm_on_duration_hours))
        print('  pwm_off_duration_hours = {0}'.format(pwm_off_duration_hours))
        print('  pattern_on_duration_days = {0}'.format(pattern_on_duration_days))
        print('  pattern_off_duration_days = {0}'.format(pattern_off_duration_days))
        print('  power = {0}'.format(power))
        start_datetime = self._start_to_start_datetime(start)
        pwm_period = (pwm_on_duration_hours + pwm_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pwm_on_duration = pwm_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pattern_period = (pattern_on_duration_days + pattern_off_duration_days)*self._MILLISECONDS_PER_DAY
        pattern_on_duration = pattern_on_duration_days*self._MILLISECONDS_PER_DAY
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm_pattern_power(relay,
                                      pwm_period,
                                      pwm_on_duration,
                                      pattern_period,
                                      pattern_on_duration,
                                      delay,
                                      power)

    def start_red_light_cycle(self,
                              relay,
                              pwm_frequency,
                              pwm_duty_cycle,
                              pattern_on_duration_hours,
                              pattern_off_duration_hours,
                              start):
        print('start_red_light_cycle:')
        print('  relay = {0}'.format(relay))
        print('  pwm_frequency = {0}'.format(pwm_frequency))
        print('  pwm_duty_cycle = {0}'.format(pwm_duty_cycle))
        print('  pattern_on_duration_hours = {0}'.format(pattern_on_duration_hours))
        print('  pattern_off_duration_hours = {0}'.format(pattern_off_duration_hours))
        start_datetime = self._start_to_start_datetime(start)
        pwm_period = 1000/pwm_frequency
        pwm_on_duration = (pwm_duty_cycle/100)*pwm_period
        pattern_period = (pattern_on_duration_hours + pattern_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pattern_on_duration = pattern_on_duration_hours*self._MILLISECONDS_PER_HOUR
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm_pattern(relay,
                                pwm_period,
                                pwm_on_duration,
                                pattern_period,
                                pattern_on_duration,
                                delay)

    def start_data_writer(self):
        if self._csv_writer is None:
            user_home_dir = os.path.expanduser('~')
            date_str = self._get_date_str()
            output_dir = os.path.join(user_home_dir,'sleep_assay_data',date_str)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            date_time_str = self._get_date_time_str()
            output_path = os.path.join(output_dir,date_time_str + '-data.txt')

            self._csv_file = open(output_path, 'w')

            # Create a new csv writer object to use as the output formatter
            self._csv_writer = csv.writer(self._csv_file,quotechar='\"',quoting=csv.QUOTE_MINIMAL)
            self._writerow(self._header)
            return output_path

    def stop(self):
        self._stop_all_pulses()

    def start(self):
        self.start_board_indicator_light_cycle(self._config['board_indicator_light']['relay'])
        experiment_start_datetime = self.start_camera_trigger(self._config['camera_trigger']['relay'],
                                                              self._config['camera_trigger']['frame_rate_hz'],
                                                              self._config['camera_trigger']['start'])
        self.start_white_light_cycle(self._config['white_light']['relay'],
                                     self._config['white_light']['pwm_on_duration_hours'],
                                     self._config['white_light']['pwm_off_duration_hours'],
                                     self._config['white_light']['pattern_on_duration_days'],
                                     self._config['white_light']['pattern_off_duration_days'],
                                     self._config['white_light']['power'],
                                     self._config['white_light']['start'])
        self.start_red_light_cycle(self._config['red_light']['relay'],
                                   self._config['red_light']['pwm_frequency_hz'],
                                   self._config['red_light']['pwm_duty_cycle_percent'],
                                   self._config['red_light']['pattern_on_duration_hours'],
                                   self._config['red_light']['pattern_off_duration_hours'],
                                   self._config['red_light']['start'])
        print('config_file_path:')
        print(self._config_file_path)
        print('data_file_path:')
        data_file_path = self.start_data_writer()
        print(data_file_path)
        print('experiment_start:')
        print('{0}-{1}-{2}-{3}-{4}-{5}'.format(experiment_start_datetime.year,
                                               experiment_start_datetime.month,
                                               experiment_start_datetime.day,
                                               experiment_start_datetime.hour,
                                               experiment_start_datetime.minute,
                                               experiment_start_datetime.second))
        experiment_duration = datetime.timedelta(self._config['experiment_duration_days'])
        experiment_end_datetime = experiment_start_datetime + experiment_duration
        print('experiment_end:')
        print('{0}-{1}-{2}-{3}-{4}-{5}'.format(experiment_end_datetime.year,
                                               experiment_end_datetime.month,
                                               experiment_end_datetime.day,
                                               experiment_end_datetime.hour,
                                               experiment_end_datetime.minute,
                                               experiment_end_datetime.second))
        row_n = 0
        video_frame = -1
        while(datetime.datetime.now() < experiment_end_datetime):
            row = []
            row.append(row_n)
            time.sleep(1/self._config['camera_trigger']['frame_rate_hz'])
            power = self._get_power()
            pwm_status = self._get_pwm_status()
            camera_trigger_on = pwm_status[self._config['camera_trigger']['relay']]
            white_light_power = power[self._config['white_light']['relay']]
            red_light_on = pwm_status[self._config['red_light']['relay']]
            if camera_trigger_on:
                video_frame += 1
            row.append(video_frame)
            date_time = self._get_date_time_str()
            row.append(date_time)
            row.append(camera_trigger_on)
            row.append(white_light_power)
            row.append(red_light_on)
            self._writerow(row)
            row_n += 1
            # print("camera_trigger =  {0}".format(pwm_status[camera_trigger_relay]))
            # print("white light =  {0}".format(power[white_light_relay]))
            # print("red_light =  {0}".format(pwm_status[red_light_relay]))


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file_path", help="Path to yaml config file.")

    args = parser.parse_args()
    config_file_path = args.config_file_path

    sa = SleepAssay(config_file_path)
    sa.start()


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
