from __future__ import print_function
import time
import datetime
import sys
from tqdm import tqdm
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
        self.print_jobs([job], in_short=False)
        self.list_tasks(job)

    def list_tasks(self, job):
        def task_info(task, result):
            return {
                'id': task.id,
                'node': task.node,
                'state': task.state,
                'result_url': '%s/output/clusrun/%s/raw' % (self.args.host, result.result_key) if result else ''
            }

        tasks = self.api.get_clusrun_tasks(job.id)
        if not tasks:
            print("No tasks created yet!")
            return

        task_results = self.wait_task_results(job, tasks)
        results = [task_info(t[0], t[1]) for t in zip(tasks, task_results)]
        print_table(['id', 'node', 'state', 'result_url'], results)

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
        self.print_jobs([job])
        self.show_task_results(job)

    def show_task_results(self, job):
        def waiter():
            sys.stderr.write('.')
            sys.stderr.flush()
            time.sleep(0.1)

        tasks = self.wait_tasks(job)
        if not tasks:
            print("No tasks created!")
            return

        task_results = self.wait_task_results(job, tasks, retry_on_failure=True)
        # Show progress bar?
        for task, result, output in self.task_outputs(job, tasks, task_results, waiter):
            print('#### %s(%s) ####' % (task.node, result.exit_code if result else ''))
            print(output or '')

    # Show progress bar?
    def wait_tasks(self, job):
        while True:
            job = self.api.get_clusrun_job(job.id)
            tasks = self.api.get_clusrun_tasks(job.id)
            if tasks or job.state in ['Finished', 'Failed', 'Canceled']:
                break
        return tasks

    def wait_task_results(self, job, tasks, retry_on_failure=False):
        total = len(tasks)
        task_results = [self.api.get_clusrun_task_result(job.id, t.id, async=True) for t in tasks]
        results = [None for i in range(total)]

        def try_get_results():
            count = 0
            for idx, task_result in enumerate(task_results):
                if results[idx] is None:
                    if task_result.ready():
                        try:
                            r = task_result.get()
                        except ApiException: # 404
                            if retry_on_failure:
                                # No result yet, try again.
                                task_results[idx] = self.api.get_clusrun_task_result(job.id, tasks[idx].id, async=True)
                            else:
                                results[idx] = False
                                count += 1
                        else:
                            results[idx] = r
                            count += 1
                else:
                    count += 1
            return count

        def progress():
            ready = 0
            while ready < total:
                s = try_get_results()
                yield s - ready
                ready = s

        def wait():
            with tqdm(total=total) as prog:
                prog.set_description("Loading tasks")
                for s in progress():
                    if s > 0:
                        prog.update(s)
                    else:
                        time.sleep(0.1)
                prog.clear()

        wait()
        return results

    def task_outputs(self, job, tasks, task_results, waiter):
        def get_last_page(result_key):
            return self.api.get_clusrun_output_in_page(result_key, offset=-1, page_size=2, async=True)

        pages = [get_last_page(t.result_key) for t in task_results]
        total = len(pages)
        done = [False for i in range(total)]
        done_count = 0
        while done_count != total:
            yielded = False
            for idx, page in enumerate(pages):
                if done[idx]:
                    continue

                if not page.ready():
                    # When last page not ready
                    continue

                result = task_results[idx]
                try:
                    output = page.get()
                except ApiException as e:
                    # When output is not created(404), try again
                    pages[idx] = get_last_page(result.result_key)
                    continue

                if not output.eof:
                    # When output is not over, try again
                    pages[idx] = get_last_page(result.result_key)
                else:
                    # When output is over
                    done[idx] = True
                    done_count += 1
                    file = self.api.get_clusrun_output(result.result_key)
                    with open(file, "r") as f:
                        yield(tasks[idx], result, f.read())
                    yielded = True

            if not yielded:
                waiter()

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

