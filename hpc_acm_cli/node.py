from __future__ import print_function
from hpc_acm_cli.command import Command
from hpc_acm_cli.utils import print_table, match_names, shorten, arrange

class Node(Command):
    @classmethod
    def profile(cls):
        return {
            'description': '''
HPC diagnostic client for querying nodes.
For help of a subcommand(list|show), execute "%(prog)s {subcommand} -h"
'''
        }

    @classmethod
    def subcommands(cls, config):
        return [
            {
                'name': 'list',
                'options': {
                    'help': 'list diagnostic jobs',
                },
                'params': [
                    {
                        'name': '--count',
                        'options': {
                            'help': 'number of nodes to query',
                            'type': int,
                            'default': config.getint('DEFAULT', 'count', fallback=None)
                        }
                    },
                    {
                        'name': '--last-id',
                        'options': { 'help': 'the node id since which(but not included) to query' }
                    },
                ],
            },
            {
                'name': 'show',
                'options': {
                    'help': 'show a single node',
                },
                'params': [
                    {
                        'name': 'id',
                        'options': { 'help': 'node id', }
                    },
                ],
            },
        ]

    def list(self):
        nodes = self.api.get_nodes(count=self.args.count, last_id=self.args.last_id)
        self.print_nodes(nodes, in_short=True)

    def show(self):
        nodes = [self.api.get_node(self.args.id)]
        self.print_nodes(nodes, in_short=False)

    def print_nodes(self, nodes, in_short=True):
        jobs = {
            'title': 'Running Jobs',
            'value': lambda n: n.running_job_count
        }
        cores = {
            'title': 'Cores',
            'value': lambda n: n.node_registration_info.core_count
        }
        memory = {
            'title': 'Memory(MB)',
            'value': lambda n: n.node_registration_info.memory_megabytes
        }
        os = {
            'title': 'OS',
            'value': lambda n: shorten(n.node_registration_info.distro_info, 60) \
                        if in_short else arrange(n.node_registration_info.distro_info, 60)
        }
        print_table(['name', 'health', 'state', jobs, cores, memory, os], nodes)

def main():
    Node.run()

if __name__ == '__main__':
    main()
