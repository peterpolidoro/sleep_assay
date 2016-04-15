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
backlight_relay = 1
backlight_on_duration_hours = 1
backlight_off_duration_hours = 1
sa.start_backlight_cycle(backlight_relay,backlight_on_duration_hours,backlight_off_duration_hours)
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
