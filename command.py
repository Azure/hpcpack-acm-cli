from parser_builder import ParserBuilder
import hpc_acm
from hpc_acm.configuration import Configuration
from hpc_acm.api_client import ApiClient
from hpc_acm.rest import ApiException

class Command:
    api_end_point = 'http://frontend.westus.azurecontainer.io/v1'

    def __init__(self, args):
        config = Configuration()
        config.host = args.host
        api_client = ApiClient(config)
        self.api = hpc_acm.DefaultApi(api_client)
        self.args = args

    @classmethod
    def build_spec(cls):
        spec = {
            'options': cls.profile,
            'params': [
                {
                    'name': '--host',
                    'options': { 'help': 'set the API end point', 'default': cls.api_end_point }
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
