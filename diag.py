#!/usr/bin/env python3

from __future__ import print_function
import argparse
from terminaltables import AsciiTable
import fnmatch
import time
import datetime
import sys
import os
import signal
import json
import hpc_acm
from hpc_acm.configuration import Configuration
from hpc_acm.api_client import ApiClient
from hpc_acm.rest import ApiException

API_END_POINT = 'http://frontend.westus.azurecontainer.io/v1'

def get_api_instance(host):
    config = Configuration()
    config.host = host
    api_client = ApiClient(config)
    return hpc_acm.DefaultApi(api_client)

def print_table(fields, collection):
    def title(f):
        return f.capitalize() if isinstance(f, str) else f['title']

    def value(element, f):
        return getattr(element, f) if isinstance(f, str) else f['value'](element)

    def to_row(element):
        return [value(element, f) for f in fields]

    headers = [title(f) for f in fields]
    rows = [to_row(e) for e in collection]
    table = AsciiTable([headers] + rows)
    print(table.table)

def print_good_nodes(job, result):
    # result = json.loads(result)
    # good_nodes = result.get("GoodNodes", None)
    # if good_nodes:
    #     good_nodes.sort()
    #     nodes = [[n] for n in good_nodes]
    #     header = 'GoodNodes(%d/%d)' % (len(nodes), len(job.target_nodes))
    #     table = AsciiTable([[header]] + nodes)
    #     print(table.table)
    print(result)

def node_cmd(args):
    api_instance = get_api_instance(args.host)
    nodes = api_instance.get_nodes()
    print_table(['name', 'health', 'state'], nodes)

def print_jobs(jobs):
    target_nodes = {
        'title': 'TargetNodes',
        'value': lambda j: len(j.target_nodes)
    }
    print_table(['id', 'name', 'state', target_nodes, 'created_at'], jobs)

def list_cmd(args):
    api_instance = get_api_instance(args.host)
    if args.id:
        job = api_instance.get_diagnostic_job(args.id)
        if args.wait:
            state = job.state
            while not state in ['Finished', 'Failed', 'Canceled']:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
                job = api_instance.get_diagnostic_job(args.id)
                state = job.state
            print('\n')
        print_jobs([job])
        result = api_instance.get_diagnostic_job_aggregation_result(args.id)
        if result:
            print_good_nodes(job, result)
    else:
        jobs = api_instance.get_diagnostic_jobs(reverse=not args.asc, count=args.count, last_id=args.last_id)
        print_jobs(jobs)

def match_names(names, pattern):
    return [n for n in names if fnmatch.fnmatch(n, pattern)]

def new_cmd(args):
    api_instance = get_api_instance(args.host)
    if args.nodes:
        nodes = args.nodes
    else:
        all = api_instance.get_nodes(count=1000000)
        names = [n.name for n in all]
        nodes = match_names(names, args.pattern)

    job = {
        "name": "Mpi Pingpong@%s" % datetime.datetime.now().isoformat(),
        "targetNodes": nodes,
        "diagnosticTest": {
            "name": "pingpong",
            "category": "mpi",
            "arguments": "[{\"name\":\"Aim\",\"value\":\"Default\"},{\"name\":\"Packet size\",\"value\":0},{\"name\":\"Mode\",\"value\":\"Tournament\"}]"
        },
    }
    # data, status, headers = api_instance.create_diagnostic_job_with_http_info(job = job)
    # job_id = getId(headers['Location'])
    job = api_instance.create_diagnostic_job(job = job)
    print_jobs([job])

def cancel_cmd(args):
    api_instance = get_api_instance(args.host)
    for id in args.ids:
        try:
            api_instance.cancel_diagnostic_job(id, job = { "request": "cancel" })
            print("Job %s is canceled." % id)
        except ApiException as e:
            print("Failed to cancel job %s. Error:\n" % id, e)

def main():
    description='''
HPC diagnostic client for querying nodes/diagnostic jobs, and creating/canceling diagnostic job.
For help of a subcommand(nodes|list|new|cancel), execute "%(prog)s -h {subcommand}"
    '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--host', help='set the API end point', default=API_END_POINT)
    subparsers = parser.add_subparsers(dest='command')

    node_cmd_parser = subparsers.add_parser('nodes', help='list nodes')

    list_cmd_parser = subparsers.add_parser('list', help='list diagnostic jobs')
    list_cmd_parser.add_argument('--count', help='number of jobs to query', type=int, default=25)
    list_cmd_parser.add_argument('--last-id', help='the job id since which(but not included) to query')
    list_cmd_parser.add_argument('--asc', help='query in id-ascending order', action='store_true')
    list_cmd_parser.add_argument('--id', help='query a single job by id')
    list_cmd_parser.add_argument('--wait', help='wait a job until it\'s over', action='store_true')

    new_cmd_parser = subparsers.add_parser('new', help='create a new diagnotic job')
    group = new_cmd_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--nodes', help='names of nodes to be tested', metavar='node', nargs='+')
    group.add_argument('--pattern', help='name pattern of nodes to be tested')

    cancel_cmd_parser = subparsers.add_parser('cancel', help='cancel a job')
    cancel_cmd_parser.add_argument('ids', help='job id', metavar='id', nargs='+')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit()

    cmd_map = {
        'nodes': 'node_cmd',
        'list': 'list_cmd',
        'new': 'new_cmd',
        'cancel': 'cancel_cmd',
    }
    cmd = cmd_map[args.command]
    globals()[cmd](args);

if __name__ == '__main__':
    main()

