#sleep_assay

Authors:

    Peter Polidoro <polidorop@janelia.hhmi.org>

License:

    BSD

##Example Usage


```python
from sleep_assay import SleepAssay
sa = SleepAssay(port='/dev/ttyUSB0')
camera_relay = 0
camera_frame_rate = 0.5
sa.start_camera_trigger(camera_relay,camera_frame_rate)
white_light_relay = 1
white_light_pwm_on_duration_hours = 12
white_light_pwm_off_duration_hours = 12
white_light_pattern_on_duration_days = 3
white_light_pattern_off_duration_days = 3
sa.start_white_light_cycle(white_light_relay,white_light_pwm_on_duration_hours,white_light_pwm_off_duration_hours,white_light_pattern_on_duration_days,white_light_pattern_off_duration_days)
red_light_relay = 2
red_light_pwm_frequency = 10
red_light_pwm_duty_cycle = 50
red_light_pattern_on_duration_hours = 12
red_light_pattern_off_duration_hours = 12
sa.start_red_light_cycle(red_light_relay,red_light_pwm_frequency,red_light_pwm_duty_cycle,red_light_pattern_on_duration_hours,red_light_pattern_off_duration_hours)
sa.stop()
```

##Installation

[Setup Python](https://github.com/janelia-pypi/python_setup)

###Linux and Mac OS X

```shell
mkdir -p ~/virtualenvs/sleep_assay
virtualenv ~/virtualenvs/sleep_assay
source ~/virtualenvs/sleep_assay/bin/activate
pip install serial_device2
```

###Windows

```shell
virtualenv C:\virtualenvs\sleep_assay
C:\virtualenvs\sleep_assay\Scripts\activate
pip install serial_device2
```
