import fnmatch
from terminaltables import AsciiTable

def match_names(names, pattern):
    return [n for n in names if fnmatch.fnmatch(n, pattern)]

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

def print_jobs(jobs):
    target_nodes = {
        'title': 'TargetNodes',
        'value': lambda j: len(j.target_nodes)
    }
    print_table(['id', 'name', 'state', target_nodes, 'created_at'], jobs)

