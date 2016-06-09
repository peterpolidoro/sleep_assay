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
    _METHOD_ID_STOP_ALL_PULSES = 1
    _METHOD_ID_GET_POWER = 2
    _METHOD_ID_GET_PWM_STATUS = 3

    _PWM_STOPPED = 0
    _PWM_RUNNING = 1

    _POWER_MAX = 255

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
                        'white_light_pwm_status',
                        'white_light_power',
                        'red_light_pwm_status']
        t_end = time.time()
        self._debug_print('Initialization time =', (t_end - t_start))

    def _debug_print(self, *args):
        if self.debug:
            print(*args)

    def _exit_sleep_assay(self):
        self.stop()

    def _flatten(self,l):
        out = []
        for item in l:
            if isinstance(item, (list, tuple)):
                out.extend(self._flatten(item))
            else:
                out.append(item)
        return out

    def _args_to_request(self,*args):
        args = self._flatten(args)
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
        response = self._serial_device.write_read(request,use_readline=True,check_write_freq=False)
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

    def _start_pwm(self,
                   relay,
                   power,
                   delay,
                   pwm_level_count,
                   periods,
                   on_durations):
        '''
        '''
        if relay < 0:
            relay = 0
        elif relay > (self._RELAY_COUNT - 1):
            relay = self._RELAY_COUNT
        power = int(power)
        delay = int(delay)
        for pwm_level in range(pwm_level_count):
            periods[pwm_level] = int(periods[pwm_level])
            on_durations[pwm_level] = int(on_durations[pwm_level])
        pwm_info = zip(periods,on_durations)

        self._send_request(self._METHOD_ID_START_PWM,
                           relay,
                           power,
                           delay,
                           pwm_level_count,
                           *pwm_info)

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
        period = 1000/self._BOARD_INDICATOR_LIGHT_FREQUENCY
        on_duration = (self._BOARD_INDICATOR_LIGHT_DUTY_CYCLE/100)*period
        self._start_pwm(relay,
                        self._POWER_MAX,
                        0,
                        1,
                        [period],
                        [on_duration])
        # self._start_pwm_frequency_duty_cycle(relay,
        #                                      self._BOARD_INDICATOR_LIGHT_FREQUENCY,
        #                                      self._BOARD_INDICATOR_LIGHT_DUTY_CYCLE,
        #                                      delay=0)

    def start_camera_trigger(self,
                             relay,
                             frame_rate,
                             start):
        print('start_camera_trigger:')
        print('  relay = {0}'.format(relay))
        print('  frame_rate = {0}'.format(frame_rate))
        start_datetime = self._start_to_start_datetime(start)
        delay = self._start_datetime_to_delay(start_datetime)
        period = 1000/frame_rate
        on_duration = (self._CAMERA_TRIGGER_DUTY_CYCLE/100)*period
        self._start_pwm(relay,
                        self._POWER_MAX,
                        delay,
                        1,
                        [period],
                        [on_duration])
        return start_datetime

    def start_white_light_cycle(self,
                                relay,
                                power,
                                pwm0_on_duration_hours,
                                pwm0_off_duration_hours,
                                pwm1_on_duration_days,
                                pwm1_off_duration_days,
                                start):
        print('start_white_light_cycle:')
        print('  relay = {0}'.format(relay))
        print('  power = {0}'.format(power))
        print('  pwm0_on_duration_hours = {0}'.format(pwm0_on_duration_hours))
        print('  pwm0_off_duration_hours = {0}'.format(pwm0_off_duration_hours))
        print('  pwm1_on_duration_days = {0}'.format(pwm1_on_duration_days))
        print('  pwm1_off_duration_days = {0}'.format(pwm1_off_duration_days))
        start_datetime = self._start_to_start_datetime(start)
        pwm0_period = (pwm0_on_duration_hours + pwm0_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pwm0_on_duration = pwm0_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pwm1_period = (pwm1_on_duration_days + pwm1_off_duration_days)*self._MILLISECONDS_PER_DAY
        pwm1_on_duration = pwm1_on_duration_days*self._MILLISECONDS_PER_DAY
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm(relay,
                        power,
                        delay,
                        2,
                        [pwm0_period,pwm1_period],
                        [pwm0_on_duration,pwm1_on_duration])

    def start_red_light_cycle(self,
                              relay,
                              pwm0_frequency,
                              pwm0_duty_cycle,
                              pwm1_on_duration_hours,
                              pwm1_off_duration_hours,
                              pwm2_on_duration_days,
                              pwm2_off_duration_days,
                              start):
        print('start_red_light_cycle:')
        print('  relay = {0}'.format(relay))
        print('  pwm0_frequency = {0}'.format(pwm0_frequency))
        print('  pwm0_duty_cycle = {0}'.format(pwm0_duty_cycle))
        print('  pwm1_on_duration_hours = {0}'.format(pwm1_on_duration_hours))
        print('  pwm1_off_duration_hours = {0}'.format(pwm1_off_duration_hours))
        print('  pwm2_on_duration_days = {0}'.format(pwm2_on_duration_days))
        print('  pwm2_off_duration_days = {0}'.format(pwm2_off_duration_days))
        start_datetime = self._start_to_start_datetime(start)
        pwm0_period = 1000/pwm0_frequency
        pwm0_on_duration = (pwm0_duty_cycle/100)*pwm0_period
        pwm1_period = (pwm1_on_duration_hours + pwm1_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pwm1_on_duration = pwm1_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pwm2_period = (pwm2_on_duration_days + pwm2_off_duration_days)*self._MILLISECONDS_PER_DAY
        pwm2_on_duration = pwm2_on_duration_days*self._MILLISECONDS_PER_DAY
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm(relay,
                        self._POWER_MAX,
                        delay,
                        3,
                        [pwm0_period,pwm1_period,pwm2_period],
                        [pwm0_on_duration,pwm1_on_duration,pwm2_on_duration])

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
                                     self._config['white_light']['power'],
                                     self._config['white_light']['pwm0_on_duration_hours'],
                                     self._config['white_light']['pwm0_off_duration_hours'],
                                     self._config['white_light']['pwm1_on_duration_days'],
                                     self._config['white_light']['pwm1_off_duration_days'],
                                     self._config['white_light']['start'])
        self.start_red_light_cycle(self._config['red_light']['relay'],
                                   self._config['red_light']['pwm0_frequency_hz'],
                                   self._config['red_light']['pwm0_duty_cycle_percent'],
                                   self._config['red_light']['pwm1_on_duration_hours'],
                                   self._config['red_light']['pwm1_off_duration_hours'],
                                   self._config['red_light']['pwm2_on_duration_days'],
                                   self._config['red_light']['pwm2_off_duration_days'],
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
            camera_trigger_on = pwm_status[self._config['camera_trigger']['relay']][0]
            white_light_pwm_status = pwm_status[self._config['white_light']['relay']][0:2]
            white_light_power = power[self._config['white_light']['relay']]
            red_light_pwm_status = pwm_status[self._config['red_light']['relay']][0:3]
            if camera_trigger_on:
                video_frame += 1
            row.append(video_frame)
            date_time = self._get_date_time_str()
            row.append(date_time)
            row.append(camera_trigger_on)
            row.append(white_light_pwm_status)
            row.append(white_light_power)
            row.append(red_light_pwm_status)
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
