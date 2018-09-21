# HPC ACM CLI

HPC Pack ACM diagnostic tools based on [HPC Pack ACM API](https://github.com/Azure/hpcpack-acm-api-python).

## Prerequisites

Python 2.7, 3.5 or 3.6.

## Installation

There're several ways to installation. Usually, you should use the PyPI way. Other ways are mainly for development purpose.

### Install from PyPI

The standard way to install the Python package is

```
python -m pip install --user hpc-acm-cli
```

Note: `python` may be `python2` or `python3` for Python 2 or Python 3 on some Linux distributions.

### Install from GitHub

You can install the latest code in development from GitHub by

```
python -m pip install --user git+https://github.com/Azure/hpcpack-acm-cli.git#egg=hpc-acm-cli
```

### Install from Source

Get the source code to local and then execute

```
python -m pip install --user -e <path-to-the-source-direcotry>
```

Note: the `-e` option enable the "editable" mode for the package so that any change you do in the source will take effect without reinstallation.

## Usage

After installation, there're 3 commands avaiable: `clusnode`, `clusdiag` and `clusrun` for cluster nodes, diagnostic jobs and general commands separately. They each have subcommands, such as `list`, `show` `new`, etc. for a type of resource. Execute a command with `-h` paramter for help message, like `clusnode -h`.

## Configuration

The above commands share a common configuration file, `.hpc_acm_cli_config`, for default values for the command line.

The file will be generated at the first time you run any of the commands. It will be put under the user's home directory(~). Typically, it's `/home/{username}` for Linux, and `C:\Users\{username}` for Windows.

The configuration file sets default values for comamnd parameters, and the default values can be overriden by those provided on command line. See comments in the file for configurable options and examples.
