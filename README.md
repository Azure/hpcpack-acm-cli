# hpc-acm-cli

HPC diagnostic client tools based on HPC ACM API.

## Dependencies

* Python 3.0 or higher, but less than 3.7. That's due to the dependent package hpc_acm. It's expected to be fixed soon.
* [hpc_acm](https://github.com/coin8086/hpc_acm_api). Install it by `pip3 install -e git+https://github.com/coin8086/hpc_acm_api.git#egg=hpc-acm`

## Installation

To install locally from source, execute

```
python3 setup.py install --user
```

under the root of the source dir.

To install from GitHub, execute

```
pip3 install -e git+https://github.com/coin8086/hpc_acm_cli.git#egg=hpc-acm-cli
```
