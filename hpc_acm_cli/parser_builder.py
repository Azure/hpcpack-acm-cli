import argparse

class ParserBuilder:
    @classmethod
    def build(cls, spec):
        parser = argparse.ArgumentParser(**spec.get('options', {}))
        params = spec.get('params', None)
        if params:
            cls.add_params(parser, params);
        subcommands = spec.get('subcommands', None)
        if subcommands:
            subparsers = parser.add_subparsers(**subcommands.get('options', {}))
            for cmd in subcommands['items']:
                subparser = subparsers.add_parser(cmd['name'], **cmd.get('options', {}))
                params = cmd.get('params', None)
                if params:
                    cls.add_params(subparser, params);
        return parser

    @classmethod
    def add_params(cls, parser, params):
        for param in params:
            group = param.get('group', False)
            if group:
                group = parser.add_mutually_exclusive_group(**param.get('options', {}))
                cls.add_params(group, param['items'])
            else:
                parser.add_argument(param['name'], **param.get('options', {}))
