# hpc-acm-cli

HPC diagnostic client tools based on HPC ACM API.

## Dependencies

* Python 3.0 or higher, but less than 3.7. That's due to the dependent package hpc_acm. It's expected to be fixed soon.
* [hpc_acm](https://github.com/coin8086/hpc_acm_api). Install it by `pip3 install -e git+https://github.com/coin8086/hpc_acm_api.git#egg=hpc-acm`

## Installation

To install locally from source, execute

```
pip3 install -e .
```

under the root of the source dir.

To install the latest release version from GitHub, execute

```
pip3 install -e git+https://github.com/coin8086/hpc_acm_cli.git@release#egg=hpc-acm-cli
```

To install the latest code in development, execute

```
pip3 install -e git+https://github.com/coin8086/hpc_acm_cli.git#egg=hpc-acm-cli
```

`pip3` is the pip for Python3 on Debian/Ubuntu. It may be just `pip` on other Linux distributions and Windows.

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

## Usage

After installation, there're 3 commands avaiable: `clusnode`, `clusdiag` and `clusrun` for cluster nodes, diagnostic jobs and general commands separately. They each have some subcommands, such as `list` and `show`, etc. Execute them with `-h` paramter for help message, like `clusnode -h`.

## Config

The commands share a common config file, `.hpc_acm_cli_config`, which is under the user's home directory(~). Usually, it's `/home/{username}` for Linux, and `c:\users\{username}` for Windows.

The config file can set default values for parameters of the commands. See comments in default(initial) config file for details. The default values are overriden by values from command line.
