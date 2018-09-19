# HPC ACM CLI

HPC diagnostic tools based on HPC ACM API.

## Prerequisites

* Python version 2.7 or higher, but less than 3.7.
* [hpcpack-acm-api-python](https://github.com/Azure/hpcpack-acm-api-python). Install it by `pip3 install  git+https://github.com/Azure/hpcpack-acm-api-python.git#egg=hpc-acm`

## Installation

### Install from Source

To install locally from source, execute the following command:

```
pip3 install <path-to-the-source-dir>
```

Note:

* `pip3` is the pip for Python3 on Debian/Ubuntu. It may be `pip`, or `pip2` for other Linux distributions, BSD and Windows, or for Python2.
* If you install it for Python2 by `pip` or `pip2`, you may need an addtional argument `--user` to install it within your home, like:
  ```
  pip install --user <path-to-the-source-dir>
  ```
* `pip3` applies `--user` by default.

### Install from GitHub

To install a release version, say, "v2.7.0" from GitHub, execute

```
pip3 install git+https://github.com/Azure/hpcpack-acm-cli.git@v2.7.0#egg=hpc-acm-cli
```

See [here](https://github.com/Azure/hpcpack-acm-cli/releases) for more releases.

To install the latest code in development, execute

```
pip3 install git+https://github.com/Azure/hpcpack-acm-cli.git#egg=hpc-acm-cli
```

Here, again, `pip3` may be `pip` or `pip2`, see notes in [Install from source](#install-from-Source).

### Special Notes for CentOS/SCL

If you enabled Software Collection(SCL) and installed Python under it, like [this artical](https://linuxize.com/post/how-to-install-python-3-on-centos-7/) said, you may have to enable SCL as *root* to install the package, otherwise you will encounter a "Permission denied" error.

Do it like this:

```
sudo su root
# yum install rh-python36
scl enable rh-python36 bash
pip install git+https://github.com/Azure/hpcpack-acm-cli.git#egg=hpc-acm-cli
```

You're assumed to have installed Python `rh-python36`. If not, replace it with yours. Also note that `pip` in above code refers to Python3's pip, and thus no need of `pip3`.

## Usage

After installation, there're 3 commands avaiable: `clusnode`, `clusdiag` and `clusrun` for cluster nodes, diagnostic jobs and general commands separately. They each have subcommands, such as `list` and `show`, etc. Execute them with `-h` paramter for help message, like `clusnode -h`.

## Config

The above commands share a common config file, `.hpc_acm_cli_config`, which is under the user's home directory(~). Usually, it's `/home/{username}` for Linux, and `c:\users\{username}` for Windows.

Note: the config file will be generated at the first time when you run any of the commands.

The config file can set default values for parameters of the commands. See comments in the config file for details. The default values set in config are overriden by values from command line.
