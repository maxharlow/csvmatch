import sys
import os
import io
import logging
import warnings
import argparse
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
        matches = matcher(args['algorithm'])(data1, data2, fields1, fields2)
        results = output(data1, data2, fields1, fields2, matches)
        print(results)
    except BaseException as e: sys.exit(e)

def arguments():
    parser = argparse.ArgumentParser(description='find matches between two CSV files')
    parser.add_argument('FILE1', nargs='?', default='-', help='the first CSV file: results will be returned where this file matches the second file -- if omitted, will accept input on STDIN')
    parser.add_argument('FILE2', nargs='?', default='-', help='the second CSV file: results will be returned where the first file matches this one')
    parser.add_argument('-1', '--fields1', nargs='+', type=str, help='one or more column names from the first file that should be used (if not provided all will be used)')
    parser.add_argument('-2', '--fields2', nargs='+', type=str, help='one or more column names from the second file that should be used (if not provided all will be used)')
    parser.add_argument('-f', '--fuzzy', nargs='?', type=str, const='bilenko', dest='algorithm', help='whether to use a fuzzy match or not')
    args = vars(parser.parse_args())
    if args['FILE1'] == '-' and args['FILE2'] == '-':
        parser.print_help()
        parser.exit(1)
    return args

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
        rows[i] = {key: items[key] for key in fields}
    return fields, rows

def matcher(fuzzy):
    if fuzzy == None: return match
    elif fuzzy == 'bilenko':
        import fuzzybilenko
        return fuzzybilenko.match
    else: raise Exception(fuzzy + ': algorithm does not exist')

def match(data1, data2, fields1, fields2):
    matches = []
    for data1key, data1values in data1.items():
        for data2key, data2values in data2.items():
            if set(data1values.values()) == set(data2values.values()): matches.append((data1key, data2key))
    return matches

def output(data1, data2, fields1, fields2, matches):
    output = io.StringIO() if sys.version_info >= (3, 0) else io.BytesIO()
    writer = csv.DictWriter(output, fields1 + fields2)
    writer.writeheader()
    for match in matches:
        row = data1.get(match[0])
        row.update(data2.get(match[1]))
        writer.writerow(row)
    return output.getvalue()

if __name__ == '__main__':
    main()
