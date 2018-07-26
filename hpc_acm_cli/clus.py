from __future__ import print_function
import time
import datetime
import sys
from hpc_acm.rest import ApiException
from hpc_acm_cli.command import Command
from hpc_acm_cli.utils import print_table, match_names, shorten, arrange

class Clusrun(Command):
    @classmethod
    def profile(cls):
        return {
            'description': '''
HPC diagnostic client for querying/creating/canceling clusrun jobs.
For help of a subcommand(list|show|new|cancel), execute "%(prog)s {subcommand} -h"
'''
        }

    @classmethod
    def subcommands(cls, config):
        return [
            {
                'name': 'list',
                'options': {
                    'help': 'list clusrun jobs',
                },
                'params': [
                    {
                        'name': '--count',
                        'options': {
                            'help': 'number of jobs to query',
                            'type': int,
                            'default': config.getint('DEFAULT', 'count', fallback=None)
                        }
                    },
                    {
                        'name': '--last-id',
                        'options': { 'help': 'the job id since which(but not included) to query' }
                    },
                    {
                        'name': '--asc',
                        'options': { 'help': 'query in id-ascending order', 'action': 'store_true' }
                    },
                ],
            },
            {
                'name': 'show',
                'options': {
                    'help': 'show a clusrun job',
                },
                'params': [
                    {
                        'name': 'id',
                        'options': { 'help': 'job id', }
                    },
                    {
                        'name': '--wait',
                        'options': { 'help': 'wait a job until it\'s over', 'action': 'store_true' }
                    },
                ],
            },
            {
                'name': 'new',
                'options': {
                    'help': 'create a new clusrun job',
                },
                'params': [
                    {
                        'group': True,
                        'items': [
                            {
                                'name': '--nodes',
                                'options': {
                                    'help': 'names of nodes to be tested. Either this or the --pattern parameter must be provided.',
                                    'metavar': 'node',
                                    'nargs': '+'
                                }
                            },
                            {
                                'name': '--pattern',
                                'options': {
                                    'help': 'name pattern of nodes to be tested. Either this or the --nodes parameter must be provided.',
                                    'default': config.get('DEFAULT', 'pattern', fallback=None)
                                }
                            },
                        ]
                    },
                    {
                        'name': 'command_line',
                        'options': { 'help': 'command to run on nodes', 'metavar': 'command' }
                    },
                ],
            },
            {
                'name': 'cancel',
                'options': {
                    'help': 'cancel a job',
                },
                'params': [
                    {
                        'name': 'ids',
                        'options': { 'help': 'job id', 'metavar': 'id', 'nargs': '+' }
                    },
                ],
            },
        ]

    def list(self):
        jobs = self.api.get_clusrun_jobs(reverse=not self.args.asc, count=self.args.count, last_id=self.args.last_id)
        self.print_jobs(jobs)

    def show(self):
        job = self.api.get_clusrun_job(self.args.id)
        if self.args.wait:
            state = job.state
            while not state in ['Finished', 'Failed', 'Canceled']:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
                job = self.api.get_clusrun_job(self.args.id)
                state = job.state
            print('\n')
        self.print_jobs([job], in_short=False)
        if job.state in ['Finished', 'Failed', 'Canceled']:
            self.list_tasks(job)

    def list_tasks(self, job):
        def new_task(t):
            try:
                r = self.api.get_clusrun_task_result(job.id, t.id)
            except ApiException: # 404
                r = None
            return {
                'id': t.id,
                'node': t.node,
                'state': t.state,
                'result_url': '%s/output/clusrun/%s/raw' % (self.args.host, r.result_key if r else '(none)')
            }
        tasks = self.api.get_clusrun_tasks(job.id)
        tasks = [new_task(t) for t in tasks]
        print_table(['id', 'node', 'state', 'result_url'], tasks)

    def new(self):
        if self.args.nodes:
            nodes = self.args.nodes
        elif self.args.pattern:
            all = self.api.get_nodes(count=1000000)
            names = [n.name for n in all]
            nodes = match_names(names, self.args.pattern)
        else:
            raise ValueError('Either nodes or pattern parameter must be provided!')

        job = {
            "name": "Command@%s" % datetime.datetime.now().isoformat(),
            "targetNodes": nodes,
            "commandLine": self.args.command_line,
        }
        job = self.api.create_clusrun_job(job = job)
        self.print_jobs([job])

    def cancel(self):
        for id in self.args.ids:
            try:
                self.api.cancel_clusrun_job(id, job = { "request": "cancel" })
                print("Job %s is canceled." % id)
            except ApiException as e:
                print("Failed to cancel job %s. Error:\n" % id, e)

    def print_jobs(self, jobs, in_short=True):
        target_nodes = {
            'title': 'Target nodes',
            'value': lambda j: len(j.target_nodes)
        }
        command = {
            'title': 'Command',
            'value': lambda j: shorten(j.command_line, 60) if in_short else arrange(j.command_line, 60)
        }
        print_table(['id', command, 'state', target_nodes, 'created_at'], jobs)

def main():
    Clusrun.run()

if __name__ == '__main__':
    main()

