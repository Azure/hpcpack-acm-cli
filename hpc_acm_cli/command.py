from __future__ import print_function
import sys
import os.path
import configparser
import argparse
from hpc_acm_cli.parser_builder import ParserBuilder
from hpc_acm_cli.arguments import Arguments
import hpc_acm
from hpc_acm.configuration import Configuration
from hpc_acm.api_client import ApiClient
from hpc_acm.rest import ApiException

class Command:
    config_path = os.path.join('~', '.hpc_acm_cli_config')

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

    @classmethod
    def run(cls):
        spec = cls.build_spec()
        parser = ParserBuilder.build(spec)
        args = parser.parse_args()
        if args.config:
            config = configparser.ConfigParser()
            if config.read(os.path.expanduser(args.config)):
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
