
#sleep_assay

Authors:

    Peter Polidoro <polidorop@janelia.hhmi.org>

License:

    BSD

##Example Usage


```shell
cd ~/sleep_assay
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

```shell
cd ~/sleep_assay/host/python
python setup.py install
```
