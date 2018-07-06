import fnmatch
from terminaltables import AsciiTable

def match_names(names, pattern):
    return [n for n in names if fnmatch.fnmatch(n, pattern)]

def titlize(str):
    return ' '.join(str.split('_')).capitalize()

def print_table(fields, collection):
    def title(f):
        return titlize(f) if isinstance(f, str) else f['title']

    def value(element, f):
        if isinstance(f, str):
            return element[f] if isinstance(element, dict) else getattr(element, f)
        else:
            return f['value'](element)

    def to_row(element):
        return [value(element, f) for f in fields]

    headers = [title(f) for f in fields]
    rows = [to_row(e) for e in collection]
    table = AsciiTable([headers] + rows)
    print(table.table)

def shorten(string, limit):
    if len(string) <= limit:
        return string
    else:
        trail = ' ...'
        return string[0:(limit - len(trail))] + trail
