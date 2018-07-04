from parser_builder import ParserBuilder
import sys
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
    def run(cls):
        spec = {
            'options': cls.profile,
            'params': [
                {
                    'name': '--host',
                    'options': { 'help': 'set the API end point', 'default': cls.api_end_point }
                },
            ],
            'subcommands': {
                'options': {
                    'dest': 'command'
                },
                'items': cls.subcommands
            },
        }
        parser = ParserBuilder.build(spec)
        args = parser.parse_args()
        if not args.command:
            parser.print_help()
            sys.exit()
        obj = cls(args)
        getattr(obj, args.command)()
