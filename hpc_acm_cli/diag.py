#!/usr/bin/env python3

from __future__ import print_function
import time
import datetime
import sys
import json
from hpc_acm.rest import ApiException
from hpc_acm_cli.command import Command
from hpc_acm_cli.utils import print_table, match_names

class Diagnostics(Command):
    profile = {
        'description': '''
HPC diagnostic client for querying/creating/canceling diagnostic jobs.
For help of a subcommand(list|new|cancel), execute "%(prog)s -h {subcommand}"
'''
    }

    subcommands = [
        {
            'name': 'list',
            'help': 'list diagnostic jobs',
            'params': [
                {
                    'name': '--count',
                    'options': { 'help': 'number of jobs to query', 'type': int, 'default': 25 }
                },
                {
                    'name': '--last-id',
                    'options': { 'help': 'the job id since which(but not included) to query' }
                },
                {
                    'name': '--asc',
                    'options': { 'help': 'query in id-ascending order', 'action': 'store_true' }
                },
                {
                    'name': '--id',
                    'options': { 'help': 'query a single job by id' }
                },
                {
                    'name': '--wait',
                    'options': { 'help': 'wait a job until it\'s over', 'action': 'store_true' }
                },
            ],
        },
        {
            'name': 'new',
            'help': 'create a new diagnotic job',
            'params': [
                {
                    'group': True,
                    'options': { 'required': True },
                    'items': [
                        {
                            'name': '--nodes',
                            'options': { 'help': 'names of nodes to be tested', 'metavar': 'node', 'nargs': '+' }
                        },
                        {
                            'name': '--pattern',
                            'options': { 'help': 'name pattern of nodes to be tested' }
                        },
                    ]
                },
            ],
        },
        {
            'name': 'cancel',
            'help': 'cancel a job',
            'params': [
                {
                    'name': 'ids',
                    'options': { 'help': 'job id', 'metavar': 'id', 'nargs': '+' }
                },
            ],
        },
    ]

    def list(self):
        if self.args.id:
            job = self.api.get_diagnostic_job(self.args.id)
            if self.args.wait:
                state = job.state
                while not state in ['Finished', 'Failed', 'Canceled']:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    time.sleep(1)
                    job = self.api.get_diagnostic_job(self.args.id)
                    state = job.state
                print('\n')
            self.print_jobs([job])
            try:
                result = self.api.get_diagnostic_job_aggregation_result(self.args.id)
            except ApiException: # 404 when aggregation result is not ready
                result = None
            if result:
                self.print_agg_result(result)
        else:
            jobs = self.api.get_diagnostic_jobs(reverse=not self.args.asc, count=self.args.count, last_id=self.args.last_id)
            self.print_jobs(jobs)

    def new(self):
        if self.args.nodes:
            nodes = self.args.nodes
        else:
            all = self.api.get_nodes(count=1000000)
            names = [n.name for n in all]
            nodes = match_names(names, self.args.pattern)

        job = {
            "name": "Mpi Pingpong@%s" % datetime.datetime.now().isoformat(),
            "targetNodes": nodes,
            "diagnosticTest": {
                "name": "pingpong",
                "category": "mpi",
                "arguments": [
                    { "name": "Aim", "value": "Default" },
                    { "name": "Packet size", "value": 0 },
                    { "name": "Mode", "value": "Tournament" },
                ]
            },
        }
        job = self.api.create_diagnostic_job(job = job)
        self.print_jobs([job])

    def cancel(self):
        for id in self.args.ids:
            try:
                self.api.cancel_diagnostic_job(id, job = { "request": "cancel" })
                print("Job %s is canceled." % id)
            except ApiException as e:
                print("Failed to cancel job %s. Error:\n" % id, e)

    def print_jobs(self, jobs):
        target_nodes = {
            'title': 'Target nodes',
            'value': lambda j: len(j.target_nodes)
        }
        print_table(['id', 'name', 'state', target_nodes, 'created_at'], jobs)

    def print_agg_result(self, result):
        if isinstance(result, str):
            result = json.loads(result)
        def get_and_print(field):
            nodes = result.get(field, None)
            if nodes is not None:
                nodes.sort()
                print("%s(%d):" % (field, len(nodes)))
                for n in nodes:
                    print(n)
        get_and_print("GoodNodes")
        get_and_print("BadNodes")

if __name__ == '__main__':
    Diagnostics.run()

