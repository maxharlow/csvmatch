import sys
import os
import io
import csv
import logging
import warnings
import argparse
import chardet
import tqdm
import csvmatch

__version__ = '1.16'

def main():
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.WARN, format='%(message)s')
    warnings.formatwarning = lambda e, *args: str(e)
    sys.stderr.write('Starting up...\n')
    try:
        file1, file2, args = arguments()
        data1, headers1 = read(*file1)
        data2, headers2 = read(*file2)
        results, keys = csvmatch.run(data1, headers1, data2, headers2, ticker=ticker, **args)
        formatted = format(results, keys)
        print(formatted)
    except BaseException as e: sys.exit(e)

def arguments():
    parser = argparse.ArgumentParser(description='find (fuzzy) matches between two CSV files')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('FILE1', nargs='?', default='-', help='the first CSV file')
    parser.add_argument('FILE2', nargs='?', default='-', help='the second CSV file')
    parser.add_argument('--enc1', type=str, help='encoding of the first file (default is to autodetect)')
    parser.add_argument('--enc2', type=str, help='encoding of the second file (default is to autodetect)')
    parser.add_argument('-1', '--fields1', nargs='+', type=str, help='one or more column names from the first CSV file that should be used (default is all columns)')
    parser.add_argument('-2', '--fields2', nargs='+', type=str, help='one or more column names from the second CSV file that should be used (default is all columns)')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='ignore case when comparing (default is case-sensitive)')
    parser.add_argument('-l', '--filter', help='filter out terms from a newline-separated file of regular expressions when comparing')
    parser.add_argument('-t', '--filter-titles', action='store_true', help='filter out a predefined list of name titles (Mr, Ms, etc) when comparing')
    parser.add_argument('-a', '--ignore-nonalpha', action='store_true', help='ignore non-alphanumeric characters when comparing')
    parser.add_argument('-n', '--as-latin', action='store_true', help='convert to latin alphabet when comparing')
    parser.add_argument('-s', '--sort-words', action='store_true', help='sort words alphabetically when comparing')
    parser.add_argument('-j', '--join', type=str, default='inner', help='the type of join to use: \'inner\', \'left-outer\', \'right-outer\', or \'full-outer\' (default is inner)')
    parser.add_argument('-o', '--output', nargs='+', type=str, help='space-separated list of fields that should be outputted, prefixed by \'1.\' or \'2.\' depending on their source file (default is the field lists if specified, otherwise all columns). Where a fuzzy matching algorithm has been used \'degree\' will add a column with a number between 0 - 1 indicating the strength of each match.')
    parser.add_argument('-f', '--fuzzy', nargs='?', type=str, const='bilenko', dest='algorithm', help='perform a fuzzy match, and an optional specified algorithm: \'bilenko\', \'levenshtein\', \'jaro\', or \'metaphone\' (default is bilenko)')
    parser.add_argument('-r', '--threshold', type=float, default=0.6, help='the threshold for a fuzzy match as a number between 0 and 1 (default is 0.6)')
    args = vars(parser.parse_args())
    if args['FILE1'] == '-' and args['FILE2'] == '-':
        parser.print_help(sys.stderr)
        parser.exit(1)
    if args['filter']:
        args['filter'] = [line[:-1] for line in io.open(args['filter'])]
    file1 = args.pop('FILE1')
    file2 = args.pop('FILE2')
    enc1 = args.pop('enc1')
    enc2 = args.pop('enc2')
    return (file1, enc1), (file2, enc2), args

def ticker(text, total):
    progress = tqdm.tqdm(bar_format=text + ' |{bar}| {percentage:3.0f}% / {remaining} left', total=total)
    return progress.update

def read(filename, encoding):
    if not os.path.isfile(filename) and filename != '-': raise Exception(filename + ': no such file')
    file = sys.stdin if filename == '-' else io.open(filename, 'rb')
    text = file.read()
    if text == '': raise Exception(filename + ': file is empty')
    if not encoding:
        encoding = chardet.detect(text[:100000])['encoding'] # can't always be relied upon
        sys.stderr.write(filename + ': autodetected character encoding as ' + encoding.upper() + '\n')
    text_decoded = text.decode(encoding)
    reader_io = io.StringIO(text_decoded, newline=None) if sys.version_info >= (3, 0) else io.BytesIO(text_decoded.encode('utf8').replace('\r\n', '\n'))
    reader = csv.reader(reader_io)
    try:
        headers = next(reader)
        data = [[value if sys.version_info >= (3, 0) else value.decode('utf8') for value in row] for row in reader]
        return data, headers
    except csv.Error as e: raise Exception(filename + ': could not read file -- try specifying the encoding')

def format(results, keys):
    lines = [[value if sys.version_info >= (3, 0) else value.encode('utf8') for value in row] for row in results]
    writer_io = io.StringIO() if sys.version_info >= (3, 0) else io.BytesIO()
    writer = csv.writer(writer_io, lineterminator='\n') # can't use dictwriter as headers are printed even when there's no results
    writer.writerow(keys)
    writer.writerows(lines)
    return writer_io.getvalue()

if __name__ == '__main__':
    main()
