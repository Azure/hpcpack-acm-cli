from __future__ import print_function
import sys
import os.path
import shutil
import configparser
import argparse
from hpc_acm_cli.parser_builder import ParserBuilder
from hpc_acm_cli.arguments import Arguments
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
    def build_spec(cls):
        options = {
            'formatter_class': argparse.ArgumentDefaultsHelpFormatter,
        }
        options.update(cls.profile)
        spec = {
            'options': options,
            'params': [
                {
                    'name': '--host',
                    'options': { 'help': 'set the API end point', 'required': True }
                },
                {
                    'name': '--config',
                    'options': { 'help': 'config file path', 'default': cls.config_path }
                },
            ],
        }
        params = getattr(cls, 'params', None)
        if params:
            spec['params'] += params
        subcommands = getattr(cls, 'subcommands', None)
        if subcommands:
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
    def make_sure_default_config(cls):
        if not os.path.exists(cls.config_path):
            path = sys.modules['hpc_acm_cli'].__file__
            dist_path = os.path.dirname(os.path.dirname(path))
            shutil.copyfile(os.path.join(dist_path, cls.config_file_name), cls.config_path)

    @classmethod
    def run(cls):
        cls.make_sure_default_config()
        spec = cls.build_spec()
        parser = ParserBuilder.build(spec)
        args = parser.parse_args()
        if args.config:
            config = configparser.ConfigParser()
            if config.read(args.config):
                args = Arguments(args, config)
            elif args.config != cls.config_path:
                print('Config file %s is not found!' % args.config, file=sys.stderr)
        obj = cls(args)
        cmd = getattr(args, 'command', None)
        if cmd:
            getattr(obj, cmd)()
        else:
            main = getattr(obj, 'main', None)
            if main:
                main()
            else:
                parser.print_help()
