# HPC Pack ACM CLI

HPC Pack ACM diagnostic tools are a set of command line tools for diagnosing HPC clusters. They're distributed in a Python package `hpc-acm-cli`, based on [HPC Pack ACM API](https://github.com/Azure/hpcpack-acm-api-python).

## Prerequisites

Python 2.7, 3.5 or 3.6 is required.

## Installation

There're several ways to install it. Usually, you should use the PyPI. Other ways are mainly for the package development.

### Install from PyPI

This is a standard way to install a Python package.

```
python -m pip install --user hpc-acm-cli
```

Note: `python` may be `python2` or `python3` for Python 2 or Python 3 for some Linux distributions.

### Install from GitHub

You can install the latest code in development from GitHub by

```
python -m pip install --user git+https://github.com/Azure/hpcpack-acm-cli.git#egg=hpc-acm-cli
```

### Install from Source

Get the source code to local and then execute

```
python -m pip install --user -e <path-to-the-source-directory>
```

Note: the `-e` option enable the "editable" mode for the package so that any change you do in the source will take effect without reinstallation.

## Usage on Linux based Distros

After installation, there're 3 commands avaiable: `clusnode`, `clusdiag` and `clusrun` for checking cluster nodes, checking/doing diagnostic jobs and checking/running general command separately. They each have subcommands, such as `list`, `show` `new`, etc..

* Execute a command with `-h` paramter to list its subcommands, like `clusnode -h`.
* For help of a subcommand, say `list`, show it like `clusnode list -h`.
* All these commands require some common parameters. They're `--host`, `--user` and `--password`. You can save the values for them in a configuration file and thus avoid entering them each time you run a command. See configuration section below for more.
* The example command lines below assumes you have the required parameters provided in the configuration file. Otherwise you'll encounter an error at runtime.

## Usage on Windows

Goto `C:\Users\{UserName}\AppData\Roaming\Python\{PythonVersion}\site-packages\hpc_acm_cli` to find dedicated programs mentioned below.
If you're not able to locate, please do the following to know the package installation directory :

- open python interpreter
- type `import hpc_acm_cli`
- enter `hpc_acm_cli.__file__` to know the package installation directory.

After installation, there're 3 commands avaiable: `node.py`, `diag.py` and `clus.py` for checking cluster nodes, checking/doing diagnostic jobs and checking/running general command separately. They each have subcommands, such as `list`, `show` `new`, etc..

### node.py

node.py is for checking cluster nodes.

For example, to list the nodes in a cluster, execute

```
node.py list
```

By default, it will list 100 nodes at once. If you prefer more, use the `--count` parameter, like

```
node.py list --count 1000
```

There's also a parameter `--last-id` for paging. Refer to command help for more.


To check a specific node

```
node.py show <node-name>
```

### diag.py

diag.py is for checking/doing diagnostic tests on a cluster.

For example, to list available diagnostic tests

```
diag.py tests
```

To run a diagnostic test

```
diag.py new <test-name> --pattern <your-node-name-pattern>
```

The `--pattern` is a glob pattern just like the file name globbing on most OSes. For example, `abc*` matches names starting with `abc`, and thus `abc`, `abc1` and `abc2` are all matched. You can use `*` to match all nodes.

You can also specify several nodes to run the test, by the `--nodes` parameter, like

```
diag.py new <test-name> --nodes "n1 n2 n3"
```

The nodes named `n1`, `n2` and `n3` are specified, spearated by a space and qouted in a pair of `"`.

To see a list of diagnostic tests

```
diag.py list
```

To check detailed result of a test

```
diag.py show <id>
```

### clus.py

clus.py is for checking/running general command on a cluster.

For example, to run a command on all nodes of the cluster:

```
clus.py new --pattern "*" "hostname && date"
```

It will execute `hostname && date` on all nodes in a cluster.


## Configuration

The above commands share a common configuration file, `.hpc_acm_cli_config`, for default values for the command line.

The file will be generated at the first time you run any of the commands. It will be put under the user's home directory(~). Typically, it's `/home/{username}` for Linux, and `C:\Users\{username}` for Windows. (check in `C:\Users\{UserName}\AppData\Roaming\Python\{PythonVersion}\site-packages\hpc_acm_cli` if it's not there in `C:\Users\{username}`)

The configuration file sets default values for command parameters, and the default values can be overriden by those provided on command line. See comments in the file for configurable options and examples.
