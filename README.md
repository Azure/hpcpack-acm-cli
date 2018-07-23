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

`pip3` is the pip for Python3.

### Special Notes for CentOS/SCL

If you enabled Software Collection(SCL) and installed Python under it, like [this artical](https://linuxize.com/post/how-to-install-python-3-on-centos-7/) said, you may have to enable SCL as *root* to install the package, otherwise you will encounter a "Permission denied" error. 

Do it like this:

```
sudo su root
# yum install rh-python36
scl enable rh-python36 bash
pip install -e git+https://github.com/coin8086/hpc_acm_cli.git#egg=hpc-acm-cli
```

You're assumed to have installed Python `rh-python36`. If not, replace it with yours. Also note that `pip` in above code refers to Python3's pip, and thus no need of `pip3`.
