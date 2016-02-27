import sys
import os
import io
import logging
import warnings
import argparse
import re
import csv
import chardet

def main():
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.WARN, format='%(message)s')
    warnings.formatwarning = lambda e, *args: str(e)
    try:
        args = arguments()
        fields1, data1 = read(args['FILE1'], args['fields1'])
        fields2, data2 = read(args['FILE2'], args['fields2'])
        processes = [
            (process_lowercase, args['ignore_case']),
            (process_filter_titles(args['ignore_case']), args['filter_titles']),
            (process_filter(args['filter'], args['ignore_case']), args['filter']),
            (process_strip_nonalpha, args['strip_nonalpha']),
            (process_sort, args['sort_words'])
        ]
        data1processed = processor(data1, processes)
        data2processed = processor(data2, processes)
        matches = matcher(args['algorithm'])(data1processed, data2processed, fields1, fields2)
        fields, data = join(args['join'], data1, data2, fields1, fields2, matches)
        results = output(data, fields)
        print(results)
    except BaseException as e: sys.exit(e)

def arguments():
    parser = argparse.ArgumentParser(description='find (fuzzy) matches between two CSV files')
    parser.add_argument('FILE1', nargs='?', default='-', help='the first CSV file')
    parser.add_argument('FILE2', nargs='?', default='-', help='the second CSV file')
    parser.add_argument('-1', '--fields1', nargs='+', type=str, help='one or more column names from the first CSV file that should be used (all columns will be used otherwise)')
    parser.add_argument('-2', '--fields2', nargs='+', type=str, help='one or more column names from the second CSV file that should be used (all columns will be used otherwise)')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='perform case-insensitive matching (it is case-sensitive otherwise)')
    parser.add_argument('-l', '--filter', help='filter out terms from a given newline-separated list of regular expressions before comparisons')
    parser.add_argument('-t', '--filter-titles', action='store_true', help='filter out name titles (Mr, Ms, etc) before comparisons')
    parser.add_argument('-a', '--strip-nonalpha', action='store_true', help='strip non-alphanumeric characters before comparisons')
    parser.add_argument('-s', '--sort-words', action='store_true', help='sort words alphabetically before comparisons')
    parser.add_argument('-j', '--join', type=str, default='inner', help='the type of join to use: \'inner\', \'left-outer\', \'right-outer\', or \'full-outer\' (default is an inner join)')
    parser.add_argument('-f', '--fuzzy', nargs='?', type=str, const='bilenko', dest='algorithm', help='use a fuzzy match, and an optional specified algorithm: \'bilenko\', \'levenshtein\', or \'metaphone\' (default is \'bilenko\')')
    args = vars(parser.parse_args())
    if args['FILE1'] == '-' and args['FILE2'] == '-':
        parser.print_help(sys.stderr)
        parser.exit(1)
    return args

def processor(data, processes):
    data_processed = data.copy()
    for process, selected in processes:
        data_processed = process(data_processed) if selected else data_processed
    return data_processed

def process_lowercase(data):
    return {key: {field: data[key][field].lower() for field in data[key]} for key in data}

def process_filter(filename, ignore_case):
    if filename == None: return
    filters = [line[:-1] for line in io.open(filename)]
    def filter(data):
        regex = re.compile('(' + '|'.join(filters) + ')', re.IGNORECASE if ignore_case else 0)
        return {key: {field: regex.sub('', data[key][field]) for field in data[key]} for key in data}
    return filter

def process_filter_titles(ignore_case):
    titles = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'csvmatch-titles.txt.py')
    return process_filter(titles, ignore_case)

def process_sort(data):
    return {key: {field: ' '.join(sorted(data[key][field].split(' '))) for field in data[key]} for key in data}

def process_strip_nonalpha(data):
    regex = re.compile('[^A-Za-z0-9 ]')
    return {key: {field: regex.sub('', data[key][field]) for field in data[key]} for key in data}

def read(filename, fields):
    if not os.path.isfile(filename) and filename != '-': raise Exception(filename + ': no such file')
    file = sys.stdin if filename == '-' else io.open(filename, 'rb')
    text = file.read()
    if text == '': raise Exception(filename + ': file is empty')
    text_decoded = text.decode(chardet.detect(text)['encoding'])
    data_io = io.StringIO(text_decoded) if sys.version_info >= (3, 0) else io.BytesIO(text_decoded.encode('utf8'))
    data = list(csv.reader(data_io))
    if len(data) < 2: raise Exception(filename + ': not enough data')
    headers = data[0]
    if fields is not None:
        for field in fields:
            if field not in headers: raise Exception(field + ': field not found')
    else: fields = headers
    reader_io = io.StringIO(text_decoded) if sys.version_info >= (3, 0) else io.BytesIO(text_decoded.encode('utf8'))
    reader = csv.DictReader(reader_io)
    rows = {}
    for i, row in enumerate(reader):
        items = dict(row.items())
        rows[i] = {key: items[key] if sys.version_info >= (3, 0) else items[key].decode('utf8') for key in fields}
    return fields, rows

def matcher(algorithm):
    if algorithm == None: return match
    elif algorithm == 'bilenko':
        import fuzzybilenko
        return fuzzybilenko.match
    elif algorithm == 'levenshtein':
        import fuzzylevenshtein
        return fuzzylevenshtein.match
    elif algorithm == 'metaphone':
        import fuzzymetaphone
        return fuzzymetaphone.match
    else: raise Exception(algorithm + ': algorithm does not exist')

def match(data1, data2, fields1, fields2):
    matches = []
    for data1key, data1values in data1.items():
        for data2key, data2values in data2.items():
            match = True
            for field1, field2 in zip(fields1, fields2):
                if data1values[field1] != data2values[field2]: match = False
            if match: matches.append((data1key, data2key))
    return matches

def join(name, data1, data2, fields1, fields2, matches):
    if name.lower() not in ['inner', 'left-outer', 'right-outer', 'full-outer']:
        raise Exception(name + ': join type not known')
    data = []
    for match in matches:
        row = []
        for field in fields1: row.append(data1.get(match[0]).get(field))
        for field in fields2: row.append(data2.get(match[1]).get(field))
        data.append([value if sys.version_info >= (3, 0) else value.encode('utf8') for value in row])
    if name.lower() == 'full-outer' or name.lower() == 'left-outer':
        for key, value in data1.items():
            if (key not in [match[0] for match in matches]):
                row = []
                for field in fields1: row.append(value.get(field))
                for field in fields2: row.append('')
                data.append([value if sys.version_info >= (3, 0) else value.encode('utf8') for value in row])
    if name.lower() == 'full-outer' or name.lower() == 'right-outer':
        for key, value in data2.items():

            if (key not in [match[1] for match in matches]):
                row = []
                for field in fields1: row.append('')
                for field in fields2: row.append(value.get(field))
                data.append([value if sys.version_info >= (3, 0) else value.encode('utf8') for value in row])
    return fields1 + fields2, data

def output(data, fields):
    output = io.StringIO() if sys.version_info >= (3, 0) else io.BytesIO()
    writer = csv.writer(output)
    writer.writerow(fields)
    writer.writerows(data)
    return output.getvalue()

if __name__ == '__main__':
    main()
