from __future__ import print_function
from hpc_acm_cli.command import Command
from hpc_acm_cli.utils import print_table, match_names, shorten

class Node(Command):
    profile = {
        'description': '''
HPC diagnostic client for querying nodes.
'''
    }

    params = [
        {
            'name': '--count',
            'options': { 'help': 'number of nodes to query', 'type': int, 'default': 25 }
        },
        {
            'name': '--last-id',
            'options': { 'help': 'the node id since which(but not included) to query' }
        },
        {
            'name': '--id',
            'options': { 'help': 'query a single node by id' }
        },
    ]

    def main(self):
        if self.args.id:
            nodes = [self.api.get_node(self.args.id)]
            self.print_nodes(nodes, in_short=False)
        else:
            nodes = self.api.get_nodes(count=self.args.count, last_id=self.args.last_id)
            self.print_nodes(nodes, in_short=True)

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
            'value': lambda n: shorten(n.node_registration_info.distro_info, 60) if in_short else n.node_registration_info.distro_info
        }
        print_table(['name', 'health', 'state', jobs, cores, memory, os], nodes)

def main():
    Node.run()

if __name__ == '__main__':
    main()
