from __future__ import print_function
import sys
import os.path
import shutil
import signal
import argparse
import getpass
from hpc_acm_cli.parser_builder import ParserBuilder
from hpc_acm_cli.easy_config import EasyConfig
from hpc_acm_cli.aad import get_access_token
import hpc_acm
from hpc_acm.configuration import Configuration
from hpc_acm.api_client import ApiClient
from hpc_acm.rest import ApiException

# Turn off warning for unverified SSL certificate, but still allow user to turn
# it on by setting envrionment variable "PYTHONWARNINGS=default".
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")

# See https://github.com/swagger-api/swagger-codegen/issues/8504
# from multiprocessing import util
# util.DEFAULT_LOGGING_FORMAT = '[%(levelname)s/%(threadName)s:%(thread)d] %(message)s'
# util.log_to_stderr(util.DEBUG)

class PasswordPrompt(argparse.Action):
    def __init__(self, option_strings, dest=None, nargs=0, default=None, required=False, type=None, metavar=None, help=None):
        super(PasswordPrompt, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            default=default,
            required=required,
            metavar=metavar,
            type=type,
            help=help
        )

    def __call__(self, parser, args, values, option_string=None):
        password = getpass.getpass()
        setattr(args, self.dest, password)

class Command:
    config_file_name = '.hpc_acm_cli_config'
    config_dir = os.path.expanduser('~')
    config_path = os.path.join(config_dir, config_file_name)

    def __init__(self, args):
        config = Configuration()
        config.host = args.host
        if args.issuer_url:
            config.access_token = get_access_token(args.issuer_url, args.client_id, args.client_secret)
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
        }
        common_params = [
            {
                'name': '--issuer-url',
                'options': { 'help': 'Issuer URL of Azure Active Directory', 'default': config.get('DEFAULT', 'issuer_url', fallback=None) }
            },
            {
                'name': '--client-id',
                'options': { 'help': 'Azure Active Directory App Id', 'default': config.get('DEFAULT', 'client_id', fallback=None) }
            },
            {
                'name': '--client-secret',
                'options': { 'help': 'Azure Active Directory App secret', 'default': config.get('DEFAULT', 'client_secret', fallback=None), 'action': PasswordPrompt }
            },
            {
                'name': '--host', # NOTE: "--base-point" seems a more meaningful name.
                'options': { 'help': 'the API end point', 'default': config.get('DEFAULT', 'host', fallback=None) }
            },
        ]
        params = cls.params(config)
        if params:
            spec['params'] = common_params + params
        subcommands = cls.subcommands(config)
        if subcommands:
            for e in subcommands:
                options = { 'formatter_class': argparse.ArgumentDefaultsHelpFormatter }
                options.update(e.get('options', {}))
                e['options'] = options
                e['params'] = common_params + e.get('params', [])
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
            dist_path = sys.modules['hpc_acm_cli'].__path__[0]
            shutil.copyfile(os.path.join(dist_path, cls.config_file_name), cls.config_path)

    @classmethod
    def read_default_config(cls):
        cls.ensure_default_config()
        config = EasyConfig()
        if not config.read(cls.config_path):
            raise FileNotFoundError('Config file %s is not found!' % args.config)
        return config

    @classmethod
    def run(cls):
        signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(100))
        try:
            config = cls.read_default_config()
        except FileNotFoundError as e:
            config = EasyConfig()
            print(e, file=sys.stderr)
        spec = cls.build_spec(config)
        parser = ParserBuilder.build(spec)
        args = parser.parse_args()
        cmd = getattr(args, 'command', None)
        if cmd:
            got = getattr(cls, cmd)
        else:
            got = getattr(cls, 'main', None)
        if got:
            obj = cls(args)
            cmd = getattr(obj, cmd)
            try:
                cmd()
            except ValueError as e:
                print('Error: %s' % e)
                parser.print_help()
                sys.exit(1)
            except Exception as e:
                print('Error: %s' % e)
                sys.exit(2)
        else:
            parser.print_help()
