# -*- coding: utf-8 -*-
from __future__ import print_function, division
import yaml
import sys
import argparse
import os
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np


class PlotConfig(object):
    '''
    '''
    _MILLISECONDS_PER_SECOND = 1000
    _SECONDS_PER_MINUTE = 60
    _MINUTES_PER_HOUR = 60
    _HOURS_PER_DAY = 24
    _MILLISECONDS_PER_HOUR = _MILLISECONDS_PER_SECOND*_SECONDS_PER_MINUTE*_MINUTES_PER_HOUR
    _MILLISECONDS_PER_DAY = _MILLISECONDS_PER_HOUR*_HOURS_PER_DAY
    _MINUTES_PER_DAY = _HOURS_PER_DAY*_MINUTES_PER_HOUR

    def __init__(self,config_file_path,*args,**kwargs):
        self._config_file_path = os.path.abspath(config_file_path)
        with open(config_file_path,'r') as config_stream:
            self._config = yaml.load(config_stream)
        # plt.figure()

    def _plot_entrainment(self):
        config = self._config['entrainment']
        t = np.linspace(0, config['duration_days'], self._MINUTES_PER_DAY, endpoint=False)

        period = config['white_light']['pwm_on_duration_hours'] + config['white_light']['pwm_off_duration_hours']
        duty_cycle = config['white_light']['pwm_on_duration_hours'] / period
        duration = config['duration_days']

        plt.subplot(2, 3, 1)
        plt.plot(t, 0.5+0.5*signal.square(2 * np.pi * 24/period * t, duty_cycle))
        plt.ylim(-0.1, 1.1)
        plt.xlabel('days')
        plt.xticks(np.linspace(0, duration, duration+1, endpoint=True))
        plt.ylabel('white light')
        plt.yticks(np.linspace(0, 1, 2, endpoint=True))
        plt.title('entrainment')

        plt.subplot(2, 3, 4)
        plt.plot(t, 0*t)
        plt.ylim(-0.1, 1.1)
        plt.xlabel('days')
        plt.xticks(np.linspace(0, duration, duration+1, endpoint=True))
        plt.ylabel('red light')
        plt.yticks(np.linspace(0, 1, 2, endpoint=True))
        plt.title('entrainment')

    def _plot_experiment(self):
        config = self._config['experiment']
        for run in range(len(config)):
            duration = config[run]['duration_days']
            t = np.linspace(0+run*duration, (run+1)*duration, self._MINUTES_PER_DAY, endpoint=False)

            period = config[run]['white_light']['pwm_on_duration_hours'] + config[run]['white_light']['pwm_off_duration_hours']
            duty_cycle = config[run]['white_light']['pwm_on_duration_hours'] / period

            plt.subplot(2, 3, 2)
            plt.plot(t, 0.5+0.5*signal.square(2 * np.pi * 24/period * t, duty_cycle))
            plt.ylim(-0.1, 1.1)
            plt.xlabel('days')
            plt.xticks(np.linspace(0, duration, duration+1, endpoint=True))
            plt.ylabel('white light')
            plt.yticks(np.linspace(0, 1, 2, endpoint=True))
            plt.title('experiment')

    def _plot_recovery(self):
        config = self._config['recovery']
        t = np.linspace(0, config['duration_days'], self._MINUTES_PER_DAY, endpoint=False)

        period = config['white_light']['pwm_on_duration_hours'] + config['white_light']['pwm_off_duration_hours']
        duty_cycle = config['white_light']['pwm_on_duration_hours'] / period
        duration = config['duration_days']

        plt.subplot(2, 3, 3)
        plt.plot(t, 0.5+0.5*signal.square(2 * np.pi * 24/period * t, duty_cycle))
        plt.ylim(-0.1, 1.1)
        plt.xlabel('days')
        plt.xticks(np.linspace(0, duration, duration+1, endpoint=True))
        plt.ylabel('white light')
        plt.yticks(np.linspace(0, 1, 2, endpoint=True))
        plt.title('recovery')

        plt.subplot(2, 3, 6)
        plt.plot(t, 0*t)
        plt.ylim(-0.1, 1.1)
        plt.xlabel('days')
        plt.xticks(np.linspace(0, duration, duration+1, endpoint=True))
        plt.ylabel('red light')
        plt.yticks(np.linspace(0, 1, 2, endpoint=True))
        plt.title('recovery')

    def plot(self):
        self._plot_entrainment()
        self._plot_experiment()
        self._plot_recovery()
        plt.show()

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file_path", help="Path to yaml config file.")

    args = parser.parse_args()
    config_file_path = args.config_file_path

    pc = PlotConfig(config_file_path)
    pc.plot()


# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
