#!/usr/bin/env python3

from __future__ import print_function
from command import Command
from utils import print_table

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
        else:
            nodes = self.api.get_nodes(count=self.args.count, last_id=self.args.last_id)
        self.print_nodes(nodes)

    def print_nodes(self, nodes):
        print_table(['name', 'health', 'state'], nodes)

if __name__ == '__main__':
    Node.run()
