from __future__ import print_function
import time
import datetime
import sys
from tqdm import tqdm
from hpc_acm.rest import ApiException
from hpc_acm_cli.command import Command
from hpc_acm_cli.utils import print_table, match_names, shorten, arrange
from hpc_acm_cli.async_op import async_wait, AsyncOp

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
                        'name': '--short',
                        'options': {
                            'help': 'do not show task output',
                            'action': 'store_true'
                        }
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
                                    'help': 'names of nodes. Multiple names are separated by spaces and quoted as one string, like "node1 node2 node3". Either this or the --pattern parameter must be provided.',
                                }
                            },
                            {
                                'name': '--pattern',
                                'options': {
                                    'help': 'name pattern of nodes. Either this or the --nodes parameter must be provided.',
                                    'default': config.get('DEFAULT', 'pattern', fallback=None)
                                }
                            },
                        ]
                    },
                    {
                        'name': 'command_line',
                        'options': { 'help': 'command to run on nodes', 'metavar': 'command' }
                    },
                    {
                        'name': '--short',
                        'options': {
                            'help': 'do no show task output.',
                            'action': 'store_true'
                        }
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
        if self.args.short:
            self.show_in_short(job)
        else:
            self.show_progressing(job)

    def new(self):
        if self.args.nodes:
            nodes = self.args.nodes.split()
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
        if self.args.short:
            self.show_in_short(job)
        else:
            self.show_progressing(job)

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

    def show_in_short(self, job):
        self.print_jobs([job], in_short=False)
        self.list_tasks(job)

    def show_progressing(self, job):
        self.print_jobs([job])
        self.show_task_outputs(job)

    def list_tasks(self, job):
        def task_info(task, result):
            return {
                'id': task.id,
                'node': task.node,
                'state': task.state,
                'result_url': '%s/output/clusrun/%s/raw' % (self.args.host, result.result_key) if result else ''
            }

        tasks = self.api.get_clusrun_tasks(job.id, count=len(job.target_nodes))
        if not tasks:
            print("No tasks created yet!")
            return

        task_results = self.wait_task_results(tasks)
        results = [task_info(t[0], t[1]) for t in zip(tasks, task_results)]
        print_table(['id', 'node', 'state', 'result_url'], results)

    class GetTaskResult(AsyncOp):
        def __init__(self, api, task):
            self.api = api
            self.async_task_result = self.api.get_clusrun_task_result(task.job_id, task.id, async=True)
            self.task_result = None
            self.ready = False

        def get_result(self):
            if self.ready:
                return self.task_result
            if not self.async_task_result.ready():
                raise AsyncOp.NotReady()
            self.ready = True
            try:
                self.task_result = self.async_task_result.get()
            except ApiException: # 404
                self.task_result = None
            return self.task_result

    def wait_task_results(self, tasks):
        return async_wait([self.__class__.GetTaskResult(self.api, t) for t in tasks], desc='Loading tasks')

    class GetTaskOutput(AsyncOp):
        def __init__(self, api, task):
            self.api = api
            self.task = task
            self.async_task_result = self.get_task_result()
            self.task_result = None
            self.async_last_page = None
            self.async_output = None
            self.output = None
            self.ready = False

        def get_task_result(self):
            return self.api.get_clusrun_task_result(self.task.job_id, self.task.id, async=True)

        def get_last_page(self):
            return self.api.get_clusrun_output_in_page(self.task_result.result_key, offset=-1, page_size=2, async=True)

        def get_output(self):
            if not self.async_output.ready():
                raise AsyncOp.NotReady()
            file = self.async_output.get()
            with open(file, "r") as f:
                self.output = f.read()
            self.ready = True

        def try_get_last_page(self):
            if not self.async_last_page.ready():
                raise AsyncOp.NotReady()
            try:
                page = self.async_last_page.get()
            except ApiException as e:
                # When output is not created(404), try again
                self.async_last_page = self.get_last_page()
            else:
                if not page.eof:
                    # When output is not over, try again
                    self.async_last_page = self.get_last_page()
                else:
                    # When output is over
                    self.async_output = self.api.get_clusrun_output(self.task_result.result_key, async=True)

        def try_get_task_result(self):
            if not self.async_task_result.ready():
                raise AsyncOp.NotReady()
            try:
                self.task_result = self.async_task_result.get()
            except ApiException as e:
                # When task result is not created(404), try again
                self.async_task_result = self.get_task_result()
            else:
                self.async_last_page = self.get_last_page()

        def get_result(self):
            if self.ready:
                return (self.task, self.task_result, self.output)
            elif self.async_output:
                self.get_output()
            elif self.async_last_page:
                self.try_get_last_page()
            else:
                self.try_get_task_result()
            raise AsyncOp.NotReady()

    def show_task_outputs(self, job):
        tasks = self.wait_tasks(job)
        if not tasks:
            print("No tasks created!")
            return

        def show_output(_, result):
            task, task_result, output = result
            print('#### %s(%s) ####' % (task.node, task_result.exit_code))
            print(output or '')

        async_wait([self.__class__.GetTaskOutput(self.api, t) for t in tasks], show_output, desc='Loading task output')

    def wait_tasks(self, job):
        while True:
            job = self.api.get_clusrun_job(job.id)
            tasks = self.api.get_clusrun_tasks(job.id, count=len(job.target_nodes))
            if tasks or job.state in ['Finished', 'Failed', 'Canceled']:
                break
            # TODO: Sleep and wait for some time here?
        return tasks

def main():
    Clusrun.run()

if __name__ == '__main__':
    main()

