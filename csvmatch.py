import argparse
import csv
import os
import sys
import io

def main():
    try:
        args = arguments()
        fields1, data1 = read(args['FILE1'], args['fields1'])
        fields2, data2 = read(args['FILE2'], args['fields2'])
        matches = match(data1, data2)
        results = output(data1, data2, fields1, fields2, matches)
        print(results)
    except Exception as e: sys.exit(e)

def arguments():
    parser = argparse.ArgumentParser(description='find matches between two CSV files')
    parser.add_argument('FILE1', nargs='?', default='-', help='the first CSV file: results will be returned where this file matches the second file -- if omitted, will accept input on STDIN')
    parser.add_argument('FILE2', nargs='?', help='the second CSV file: results will be returned where the first file matches this one')
    parser.add_argument('-1', '--fields1', nargs='+', type=str, help='one or more column names from the first file that should be used (if not provided all will be used)')
    parser.add_argument('-2', '--fields2', nargs='+', type=str, help='one or more column names from the second file that should be used (if not provided all will be used)')
    args = vars(parser.parse_args())
    if not args['FILE2']:
        parser.print_help()
        parser.exit(1)
    return args

def read(filename, fields):
    if not os.path.isfile(filename) and filename != '-': raise Exception(filename + ': no such file')
    file = sys.stdin if filename == '-' else io.open(filename)
    text = file.read()
    data = list(csv.reader(io.StringIO(text)))
    if len(data) < 2: raise Exception(filename + ': not enough data')
    headers = data[0]
    if fields is not None:
        for field in fields:
            if field not in headers: raise Exception(field + ': field not found')
    else: fields = headers
    reader = csv.DictReader(io.StringIO(text))
    rows = {}
    for (i, row) in enumerate(reader):
        items = dict(row.items())
        rows['%s|%s' % (filename, i)] = { key: items[key] for key in fields }
    return fields, dict(rows)

def match(data1, data2):
    matches = []
    for data1Key, data1Values in data1.items():
        for data2Key, data2Values in data2.items():
            if set(data1Values.values()) == set(data2Values.values()): matches.append((data1Key, data2Key))
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
