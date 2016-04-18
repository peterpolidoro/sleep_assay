#sleep_assay

Authors:

    Peter Polidoro <polidorop@janelia.hhmi.org>

License:

    BSD

##Example Usage


```shell
source ~/virtualenvs/sleep_assay/bin/activate
python sleep_assay.py example_config.yaml
```

```python
from sleep_assay import SleepAssay
sa = SleepAssay('example_config.yaml')
sa.start()
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
pip install pyyaml
```

###Windows

```shell
virtualenv C:\virtualenvs\sleep_assay
C:\virtualenvs\sleep_assay\Scripts\activate
pip install serial_device2
pip install pyyaml
```
