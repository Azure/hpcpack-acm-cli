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

