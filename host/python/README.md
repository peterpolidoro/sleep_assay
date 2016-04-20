#sleep_assay

Authors:

    Peter Polidoro <polidorop@janelia.hhmi.org>

License:

    BSD

##Example Usage


Open terminal on linux/osx or git bash on windows.

```shell
sleep_assay.py ~/sleep_assay/config/example_config.yaml
```

Press ctrl-c in terminal window or close terminal window to stop.

In ipython or the python command shell:

```python
from sleep_assay import SleepAssay
sa = SleepAssay('example_config.yaml')
sa.start()
sa.stop()
```

##Installation

[Setup Python](https://github.com/janelia-pypi/python_setup)

```shell
cd ~/sleep_assay/host/python
python setup.py install
```
