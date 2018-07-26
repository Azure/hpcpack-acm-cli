from __future__ import print_function
import sys
import os.path
import shutil
import configparser
import argparse
from hpc_acm_cli.parser_builder import ParserBuilder
import hpc_acm
from hpc_acm.configuration import Configuration
from hpc_acm.api_client import ApiClient
from hpc_acm.rest import ApiException

class Command:
    config_file_name = '.hpc_acm_cli_config'
    config_dir = os.path.expanduser('~')
    config_path = os.path.join(config_dir, config_file_name)

    def __init__(self, args):
        config = Configuration()
        config.host = args.host
        api_client = ApiClient(config)
        self.api = hpc_acm.DefaultApi(api_client)
        self.args = args

    @classmethod
    def profile(cls):
        return {}

    @classmethod
    def params(cls, config):
        return []

    @classmethod
    def subcommands(cls, config):
        return []

    @classmethod
    def build_spec(cls, config):
        options = {
            'formatter_class': argparse.ArgumentDefaultsHelpFormatter,
        }
        options.update(cls.profile())
        spec = {
            'options': options,
            'params': [
                {
                    'name': '--host',
                    'options': { 'help': 'set the API end point', 'default': config.get('DEFAULT', 'host', fallback=None) }
                },
            ],
        }
        params = cls.params(config)
        if params:
            spec['params'] += params
        subcommands = cls.subcommands(config)
        if subcommands:
            for e in subcommands:
                options = { 'formatter_class': argparse.ArgumentDefaultsHelpFormatter }
                options.update(e['options'])
                e['options'] = options
            spec['subcommands'] = {
                'options': {
                    'dest': 'command' # args.command
                },
                'items': subcommands
            }
        return spec

    # The reason to have this method is explained in setup.py of the containing package.
    # Simply put, the Python package installation can't copy the default config to user home.
    @classmethod
    def ensure_default_config(cls):
        if not os.path.exists(cls.config_path):
            path = sys.modules['hpc_acm_cli'].__file__
            dist_path = os.path.dirname(os.path.dirname(path))
            shutil.copyfile(os.path.join(dist_path, cls.config_file_name), cls.config_path)

    @classmethod
    def read_default_config(cls):
        cls.ensure_default_config()
        config = configparser.ConfigParser()
        if not config.read(cls.config_path):
            raise FileNotFoundError('Config file %s is not found!' % args.config)
        return config

    @classmethod
    def run(cls):
        try:
            config = cls.read_default_config()
        except FileNotFoundError as e:
            config = configparser.ConfigParser()
            print(e, file=sys.stderr)
        spec = cls.build_spec(config)
        parser = ParserBuilder.build(spec)
        args = parser.parse_args()
        obj = cls(args)
        cmd = getattr(args, 'command', None)
        if cmd:
            cmd = getattr(obj, cmd)
        else:
            cmd = getattr(obj, 'main', None)
        if cmd:
            try:
                cmd()
            except ValueError as e:
                print('Error: %s' % e)
                parser.print_help()
                sys.exit(1)
            except ApiException as e:
                print('Error: %s' % e)
                sys.exit(2)
        else:
            parser.print_help()
