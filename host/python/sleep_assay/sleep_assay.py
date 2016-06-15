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
import numpy as np
import matplotlib.pyplot as plt
import math

from serial_device2 import SerialDevice, SerialDevices, find_serial_device_ports, WriteFrequencyError

DEBUG = False
QUICK_TEST = False
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
    if not QUICK_TEST:
        _MILLISECONDS_PER_SECOND = 1000
    else:
        _MILLISECONDS_PER_SECOND = 1000/3600
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
            try:
                kwargs['port'] = self._config['relay_board_serial_port']['linux']
            except KeyError:
                raise RuntimeError('Must specify linux serial port in config file!')
        elif os_type == 'Windows':
            try:
                kwargs['port'] = self._config['relay_board_serial_port']['windows']
            except KeyError:
                raise RuntimeError('Must specify windows serial port in config file!')
        elif os_type == 'Darwin':
            try:
                kwargs['port'] = self._config['relay_board_serial_port']['osx']
            except KeyError:
                raise RuntimeError('Must specify osx serial port in config file!')
        t_start = time.time()
        self._serial_device = SerialDevice(*args,**kwargs)
        atexit.register(self._exit_sleep_assay)
        time.sleep(self._RESET_DELAY)
        self._csv_file = None
        self._csv_writer = None
        self._video_frame = -1
        self._state = 'initialization'
        self._header = ['video_frame',
                        'date_time',
                        'state',
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
                   count,
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
        count = int(count)
        for pwm_level in range(pwm_level_count):
            periods[pwm_level] = int(periods[pwm_level])
            on_durations[pwm_level] = int(on_durations[pwm_level])
        pwm_info = zip(periods,on_durations)

        self._send_request(self._METHOD_ID_START_PWM,
                           relay,
                           power,
                           delay,
                           count,
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

    def _print_datetime(self,dt):
        print('    {0}-{1}-{2}-{3}-{4}-{5}'.format(dt.year,
                                                   dt.month,
                                                   dt.day,
                                                   dt.hour,
                                                   dt.minute,
                                                   dt.second))

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
        delay = int(1000*delta.total_seconds())
        if delay < 0:
            start_datetime = now_datetime
        return start_datetime

    def _start_datetime_to_delay(self,start_datetime):
        now_datetime = datetime.datetime.now()
        delta = start_datetime - now_datetime
        delay = int(1000*delta.total_seconds())
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
                        -1,
                        1,
                        [period],
                        [on_duration])

    def start_camera_trigger(self,
                             relay,
                             frame_rate,
                             delay):
        print('start_camera_trigger:')
        print('  relay = {0}'.format(relay))
        print('  frame_rate = {0}'.format(frame_rate))
        period = 1000/frame_rate
        on_duration = (self._CAMERA_TRIGGER_DUTY_CYCLE/100)*period
        self._start_pwm(relay,
                        self._POWER_MAX,
                        delay,
                        -1,
                        1,
                        [period],
                        [on_duration])

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

    def _duration_days_to_duration_datetime(self,duration_days):
        duration_datetime = datetime.timedelta(duration_days/(1000/self._MILLISECONDS_PER_SECOND))
        return duration_datetime

    def start_entrainment(self,start_datetime,config):
        print('entrainment:')
        print('  start:')
        self._print_datetime(start_datetime)
        duration_days = config['duration_days']
        relay = self._config['relays']['white_light']
        power = config['white_light']['power']
        pwm0_on_duration_hours = config['white_light']['pwm0_on_duration_hours']
        pwm0_off_duration_hours = config['white_light']['pwm0_off_duration_hours']
        pwm0_period_hours = pwm0_on_duration_hours + pwm0_off_duration_hours
        pwm0_period = pwm0_period_hours*self._MILLISECONDS_PER_HOUR
        pwm0_on_duration = pwm0_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pwm0_period_days = pwm0_period_hours/self._HOURS_PER_DAY
        count = duration_days/pwm0_period_days
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm(relay,
                        power,
                        delay,
                        count,
                        1,
                        [pwm0_period],
                        [pwm0_on_duration])
        duration_datetime = self._duration_days_to_duration_datetime(duration_days)
        end_datetime = start_datetime + duration_datetime
        print('  end:')
        self._print_datetime(end_datetime)
        return end_datetime

    def start_experiment_run(self,run,start_datetime,config):
        print('experiment run {0}:'.format(run))
        print('  start:')
        self._print_datetime(start_datetime)
        duration_days = config['duration_days']

        # white light
        relay = self._config['relays']['white_light']
        power = config['white_light']['power']
        pwm0_on_duration_hours = config['white_light']['pwm0_on_duration_hours']
        pwm0_off_duration_hours = config['white_light']['pwm0_off_duration_hours']
        pwm0_period = (pwm0_on_duration_hours + pwm0_off_duration_hours)*self._MILLISECONDS_PER_HOUR
        pwm0_on_duration = pwm0_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pwm1_on_duration_days = config['white_light']['pwm1_on_duration_days']
        pwm1_off_duration_days = config['white_light']['pwm1_off_duration_days']
        pwm1_period_days = pwm1_on_duration_days + pwm1_off_duration_days
        pwm1_period = pwm1_period_days*self._MILLISECONDS_PER_DAY
        pwm1_on_duration = pwm1_on_duration_days*self._MILLISECONDS_PER_DAY
        count = duration_days/pwm1_period_days
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm(relay,
                        power,
                        delay,
                        count,
                        2,
                        [pwm0_period,pwm1_period],
                        [pwm0_on_duration,pwm1_on_duration])

        # red light
        relay = self._config['relays']['red_light']
        pwm0_frequency = config['red_light']['pwm0_frequency_hz']
        pwm0_duty_cycle = config['red_light']['pwm0_duty_cycle_percent']
        pwm0_period = 1000/pwm0_frequency
        pwm0_on_duration = (pwm0_duty_cycle/100)*pwm0_period
        pwm1_on_duration_hours = config['red_light']['pwm1_on_duration_hours']
        pwm1_off_duration_hours = config['red_light']['pwm1_off_duration_hours']
        pwm1_period_hours = pwm1_on_duration_hours + pwm1_off_duration_hours
        pwm1_period = pwm1_period_hours*self._MILLISECONDS_PER_HOUR
        pwm1_on_duration = pwm1_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pwm1_period_days = pwm1_period_hours/self._HOURS_PER_DAY
        delay_days = config['red_light']['delay_days']
        count = math.ceil((duration_days - delay_days)/pwm1_period_days)
        duration_datetime = self._duration_days_to_duration_datetime(delay_days)
        red_start_datetime = start_datetime + duration_datetime
        delay = self._start_datetime_to_delay(red_start_datetime)
        power = 255
        self._start_pwm(relay,
                        power,
                        delay,
                        count,
                        2,
                        [pwm0_period,pwm1_period],
                        [pwm0_on_duration,pwm1_on_duration])

        duration_datetime = self._duration_days_to_duration_datetime(duration_days)
        end_datetime = start_datetime + duration_datetime
        print('  end:')
        self._print_datetime(end_datetime)
        return end_datetime

    def start_recovery(self,start_datetime,config):
        print('recovery:')
        print('  start:')
        self._print_datetime(start_datetime)
        duration_days = config['duration_days']
        relay = self._config['relays']['white_light']
        power = config['white_light']['power']
        pwm0_on_duration_hours = config['white_light']['pwm0_on_duration_hours']
        pwm0_off_duration_hours = config['white_light']['pwm0_off_duration_hours']
        pwm0_period_hours = pwm0_on_duration_hours + pwm0_off_duration_hours
        pwm0_period = pwm0_period_hours*self._MILLISECONDS_PER_HOUR
        pwm0_on_duration = pwm0_on_duration_hours*self._MILLISECONDS_PER_HOUR
        pwm0_period_days = pwm0_period_hours/self._HOURS_PER_DAY
        count = duration_days/pwm0_period_days
        delay = self._start_datetime_to_delay(start_datetime)
        self._start_pwm(relay,
                        power,
                        delay,
                        count,
                        1,
                        [pwm0_period],
                        [pwm0_on_duration])
        duration_datetime = self._duration_days_to_duration_datetime(duration_days)
        end_datetime = start_datetime + duration_datetime
        print('  end:')
        self._print_datetime(end_datetime)
        return end_datetime

    def _write_data(self):
        time_start = time.time()
        power = self._get_power()
        pwm_status = self._get_pwm_status()
        camera_trigger_on = pwm_status[self._config['relays']['camera_trigger']][1]
        white_light_pwm_status = pwm_status[self._config['relays']['white_light']][0:3]
        white_light_power = power[self._config['relays']['white_light']]
        red_light_pwm_status = pwm_status[self._config['relays']['red_light']][1]
        if camera_trigger_on:
            self._video_frame += 1
            date_time = self._get_date_time_str()
            if ((self._white_light_power_prev != white_light_power) or
                (self._red_light_pwm_status_prev != red_light_pwm_status) or
                (self._state_prev != self._state)):
                if ((not self._prev_written) and
                    (self._white_light_power_prev is not None) and
                    (self._red_light_pwm_status_prev is not None) and
                    (self._date_time_prev is not None)):
                    row = []
                    row.append(self._video_frame - 1)
                    row.append(self._date_time_prev)
                    row.append(self._state_prev)
                    row.append(self._white_light_power_prev)
                    row.append(self._red_light_pwm_status_prev)
                    self._writerow(row)
                row = []
                row.append(self._video_frame)
                row.append(date_time)
                row.append(self._state)
                row.append(white_light_power)
                row.append(red_light_pwm_status)
                self._writerow(row)
                self._prev_written = True
            else:
                self._prev_written = False
            self._white_light_power_prev = white_light_power
            self._red_light_pwm_status_prev = red_light_pwm_status
            self._state_prev = self._state
            self._date_time_prev = date_time

        time_stop = time.time()
        time_sleep = 1/self._config['camera_trigger']['frame_rate_hz'] - (time_stop - time_start)
        if time_sleep > 0:
            time.sleep(time_sleep)

    def plot_data(self,data_file_path):
        fig = plt.figure()
        filename = os.path.split(data_file_path)[1]
        fig.suptitle(filename, fontsize=14, fontweight='bold')
        self._data_file_path = os.path.abspath(data_file_path)
        with open(self._data_file_path,'r') as fid:
            header = fid.readline().rstrip().split(',')

        dt = np.dtype({'names':header,'formats':['S25']*len(header)})
        self._numpy_data = np.loadtxt(self._data_file_path,dtype=dt,delimiter=",",skiprows=1)

        scale_factor = 1000/(self._config['camera_trigger']['frame_rate_hz']*self._MILLISECONDS_PER_DAY)
        t = np.uint32(self._numpy_data['video_frame'])*scale_factor

        # white light
        power = np.uint8(self._numpy_data['white_light_power'])
        y_max = 255
        plt.subplot(2, 1, 1)
        plt.plot(t, power)
        plt.ylim(-0.1, y_max+45)
        plt.ylabel('white light power')
        plt.xlabel('days')
        duration_days = int(t.max())
        plt.xticks(np.linspace(0, duration_days+1, 2*duration_days+3, endpoint=True))
        plt.grid(True)
        marker_half_thickness = 0.025
        start = 0
        stop = self._config['entrainment']['duration_days'] - marker_half_thickness
        plt.axvspan(start, stop, color='y', alpha=0.5, lw=0)
        plt.text(start + (stop-start)/2, y_max+25, 'entrainment', fontsize=15, horizontalalignment='center')
        start = stop
        stop = start + 2*marker_half_thickness
        plt.axvspan(start, stop, color='k', alpha=0.5, lw=0)
        run = 0
        for run_config in self._config['experiment']:
            start = stop
            stop = start + run_config['duration_days'] - 2*marker_half_thickness
            plt.axvspan(start, stop, color='g', alpha=0.5, lw=0)
            plt.text(start + (stop-start)/2, y_max+25, 'experiment run {0}'.format(run), fontsize=15, horizontalalignment='center')
            start = stop
            stop = start + 2*marker_half_thickness
            plt.axvspan(start, stop, color='k', alpha=0.5, lw=0)
            run += 1
        start = stop
        stop = start + self._config['recovery']['duration_days'] - marker_half_thickness
        plt.axvspan(start, stop, color='r', alpha=0.5, lw=0)
        plt.text(start + (stop-start)/2, y_max+25, 'recovery', fontsize=15, horizontalalignment='center')
        start = stop
        stop = start + marker_half_thickness
        plt.axvspan(start, stop, color='k', alpha=0.5, lw=0)

        # red light
        red_light_pwm_status = np.uint8(self._numpy_data['red_light_pwm_status'])
        y_max = 1
        plt.subplot(2, 1, 2)
        plt.plot(t, red_light_pwm_status)
        plt.ylim(-0.1, y_max+0.25)
        plt.ylabel('red light pwm status')
        plt.xlabel('days')
        duration_days = int(t.max())
        plt.xticks(np.linspace(0, duration_days+1, 2*duration_days+3, endpoint=True))
        plt.grid(True)
        marker_half_thickness = 0.025
        start = 0
        stop = self._config['entrainment']['duration_days'] - marker_half_thickness
        plt.axvspan(start, stop, color='y', alpha=0.5, lw=0)
        plt.text(start + (stop-start)/2, y_max+0.1, 'entrainment', fontsize=15, horizontalalignment='center')
        start = stop
        stop = start + 2*marker_half_thickness
        plt.axvspan(start, stop, color='k', alpha=0.5, lw=0)
        run = 0
        for run_config in self._config['experiment']:
            start = stop
            stop = start + run_config['duration_days'] - 2*marker_half_thickness
            plt.axvspan(start, stop, color='g', alpha=0.5, lw=0)
            plt.text(start + (stop-start)/2, y_max+0.1, 'experiment run {0}'.format(run), fontsize=15, horizontalalignment='center')
            start = stop
            stop = start + 2*marker_half_thickness
            plt.axvspan(start, stop, color='k', alpha=0.5, lw=0)
            run += 1
        start = stop
        stop = start + self._config['recovery']['duration_days'] - marker_half_thickness
        plt.axvspan(start, stop, color='r', alpha=0.5, lw=0)
        plt.text(start + (stop-start)/2, y_max+25, 'recovery', fontsize=15, horizontalalignment='center')
        start = stop
        stop = start + marker_half_thickness
        plt.axvspan(start, stop, color='k', alpha=0.5, lw=0)

        plt.show()

    def run(self):
        self.stop()
        print('config_file_path:')
        print(self._config_file_path)
        print('data_file_path:')
        data_file_path = self.start_data_writer()
        print(data_file_path)
        self.start_board_indicator_light_cycle(self._config['relays']['board_indicator_light'])
        entrainment_start_datetime = self._start_to_start_datetime(self._config['start'])
        delay = self._start_datetime_to_delay(entrainment_start_datetime)
        self._video_frame = -1
        self.start_camera_trigger(self._config['relays']['camera_trigger'],
                                  self._config['camera_trigger']['frame_rate_hz'],
                                  delay)
        self._state = 'entrainment'
        entrainment_end_datetime = self.start_entrainment(entrainment_start_datetime,
                                                          self._config['entrainment'])
        self._white_light_power_prev = None
        self._red_light_pwm_status_prev = None
        self._state_prev = None
        self._prev_written = False
        self._date_time_prev = None
        while(datetime.datetime.now() < entrainment_end_datetime):
            self._write_data()

        run_start_datetime = entrainment_end_datetime
        for run in range(len(self._config['experiment'])):
            self._state = 'experiment_run{0}'.format(run)
            run_end_datetime = self.start_experiment_run(run,
                                                         run_start_datetime,
                                                         self._config['experiment'][run])
            while(datetime.datetime.now() < run_end_datetime):
                self._write_data()
            run_start_datetime = run_end_datetime

        self._state = 'recovery'
        recovery_start_datetime = run_end_datetime
        recovery_end_datetime = self.start_recovery(recovery_start_datetime,
                                                    self._config['recovery'])
        while(datetime.datetime.now() < recovery_end_datetime):
            self._write_data()


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file_path", help="Path to yaml config file.")
    parser.add_argument('-p',"--plot-data", help="Path to csv data file.")

    args = parser.parse_args()
    config_file_path = args.config_file_path

    sa = SleepAssay(config_file_path)
    if args.plot_data:
        sa.plot_data(args.plot_data)
    else:
        sa.run()


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
