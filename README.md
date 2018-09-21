# HPC ACM CLI

HPC diagnostic tools based on HPC ACM API.

## Prerequisites

Python version 2.7 or higher, but less than 3.7.

## Dependencies

[hpcpack-acm-api-python](https://github.com/Azure/hpcpack-acm-api-python).

This will be installed automatically when you install the CLI package.

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

You can also pick a release version, say, "v2.7.0" from GitHub, by

```
python -m pip install --user git+https://github.com/Azure/hpcpack-acm-cli.git@v2.7.0#egg=hpc-acm-cli
```

See [here](https://github.com/Azure/hpcpack-acm-cli/releases) for more releases.

### Install from Source

First get the source code to local, and then execute the following command

```
python -m pip install --user <path-to-the-source-dir>
```

## Usage

After installation, there're 3 commands avaiable: `clusnode`, `clusdiag` and `clusrun` for cluster nodes, diagnostic jobs and general commands separately. They each have subcommands, such as `list`, `show` `new`, etc. for a type of resource. Execute a command with `-h` paramter for help message, like `clusnode -h`.

## Configuration

The above commands share a common configuration file, `.hpc_acm_cli_config`, for default values for the command line.

The file will be generated at the first time you run any of the commands. It will be put under the user's home directory(~). Typically, it's `/home/{username}` for Linux, and `C:\Users\{username}` for Windows.

The configuration file sets default values for comamnd parameters, and the default values can be overriden by those provided on command line. See comments in the file for configurable options and examples.
