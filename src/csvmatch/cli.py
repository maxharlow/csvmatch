from typing import Optional, cast
import sys
import os
import io
import re
import signal
import importlib.metadata
import traceback
import argparse
import chardet
import polars
import textmatch

from . import cli_renderer
from .typings import (
    ArrowDataframe,
    PolarsDataframe,
    Alert
)

def main() -> None:
    file1, file2, args, verbose = arguments()
    alert, progress, finalise = cli_renderer.setup(verbose)
    def interrupt(signal, frame):
        finalise('interrupt')
        raise SystemExit(1)
    signal.signal(signal.SIGINT, interrupt)
    try:
        source1 = read(*file1, alert)
        source2 = read(*file2, alert)
        results = textmatch.run(source1, source2, **{**args, 'progress': progress, 'alert': alert})
        finalise('complete')
        format(results)
        sys.exit()
    except Exception as e:
        finalise('error', traceback.format_exc().strip() if verbose else str(e))
        sys.exit(1)

def arguments() -> tuple[tuple[str, str], tuple[str, str], dict[str, str], bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=importlib.metadata.version('csvmatch'))
    parser.add_argument('-V', '--verbose', action='store_true', help='print more information')
    parser.add_argument('FILE1', help='first file')
    parser.add_argument('FILE2', help='second file')
    parser.add_argument('--enc1', type=str, metavar='ENCODING', help='encoding of the first file (default: autodetect)')
    parser.add_argument('--enc2', type=str, metavar='ENCODING', help='encoding of the second file (default: autodetect)')
    parser.add_argument('-1', '--fields1', action='append', nargs='+', type=str, metavar='FIELD',
                        help='column names from the first file to match on, space-separated (default: all columns)')
    parser.add_argument('-2', '--fields2', action='append', nargs='+', type=str, metavar='FIELD',
                        help='column names from the second file to match on, space-separated (default: all columns)')
    parser.add_argument('-i', '--ignore', action='append', nargs='*', type=str, default=[], dest='ignores', metavar='PROPERTY',
                        help='properties to ignore, space-separated: \'case\' (c), \'nonalpha\' (na), \'nonlatin\' (nl), \'words-leading\' (wl), \'words-tailing\' (wt), \'words-order\' (wo), \'titles\' (t), or \'regex=EXPRESSION\' (r=EXPRESSION) where EXPRESSION is a regular expression')
    parser.add_argument('-j', '--join', type=str, default='inner', metavar='TYPE', choices=['inner', 'left-outer', 'right-outer', 'full-outer'],
                        help='the type of join to use: \'inner\', \'left-outer\', \'right-outer\', or \'full-outer\' (default: \'inner\')')
    parser.add_argument('-m', '--method', nargs='+', type=str, default=['literal'], dest='methods', metavar='METHOD', choices=['literal', 'levenshtein', 'leven', 'jaro', 'metaphone', 'bilenko'],
                        help='the matching method to use: \'literal\', \'levenshtein\', \'jaro\', \'metaphone\', or \'bilenko\' (default: \'literal\')')
    parser.add_argument('-t', '--threshold', nargs='+', type=float, default=[0.6], dest='thresholds', metavar='THRESHOLD',
                        help='the threshold for a match to be a match, as a number between 0 and 1 (default: 0.6)')
    parser.add_argument('-o', '--output', nargs='+', type=str, metavar='FIELD',
                        help='fields to include in the output, space-separated and prefixed by \'1.\' or \'2.\' depending on their source file - use \'1*\' or \'2*\' to include all columns from either file, and \'degree\' to add a column showing the strength or each match (default: all columns)')
    args = vars(parser.parse_args(None if sys.argv[1:] else ['--help']))
    if len(args['ignores']) == 0:
        args['ignores'] = [[]]
    for block in args['ignores']:
        for i, property in enumerate(block):
            if property == 'c': block[i] = 'case'
            if property == 'na': block[i] = 'nonalpha'
            if property == 'nl': block[i] = 'nonlatin'
            if property == 'wl': block[i] = 'words-leading'
            if property == 'wt': block[i] = 'words-tailing'
            if property == 'wo': block[i] = 'words-order'
            if property == 't': block[i] = 'titles'
            if property.startswith('r='): block[i] = re.sub('^r=', 'regex=', block[i])
            if property.startswith('regex='):
                ignore_regex_filename = re.sub(r'^regex=', '', property)
                if os.path.exists(ignore_regex_filename):
                    block[i] = 'regex=' + '|'.join([line[:-1] for line in io.open(ignore_regex_filename)])
    for i, method in enumerate(args['methods']):
        if method == 'leven': args['methods'][i] = 'levenshtein'
    file1 = args.pop('FILE1')
    file2 = args.pop('FILE2')
    enc1 = args.pop('enc1')
    enc2 = args.pop('enc2')
    verbose = args.pop('verbose')
    return (file1, enc1), (file2, enc2), args, verbose

def read(filename: str, encoding: Optional[str], alert: Alert) -> PolarsDataframe:
    if not os.path.isfile(filename) and filename != '-': raise Exception(f'{filename}: no such file')
    if os.path.getsize(filename) == 0: raise Exception(f'{filename}: file is empty')
    def disambiguate(columns: list[str]) -> list[str]:
        columns = columns.copy() # so we don't overwrite the original
        columns_clean = [re.sub(r'_duplicated_[0-9]+$', '', column) for column in columns]
        columns_counts = {i: columns_clean.count(i) for i in columns_clean}
        for column, count in columns_counts.items():
            if count == 1: continue
            alert(f'{filename}: there are multiple columns named "{column}"; they will be renamed')
            for i in range(count - 1):
                columns[columns.index(f'{column}_duplicated_{i}')] = f'{column}{i + 1}'
        return columns
    if filename.split('.').pop().lower() == 'parquet':
        columns = polars.read_parquet(filename, n_rows=0).columns
        columns_new = disambiguate(columns)
        data = polars.read_parquet(filename)
        data = data.rename(dict(zip(columns, columns_new)))
        return data
    if not encoding:
        detector = chardet.universaldetector.UniversalDetector()
        file = io.open(filename, 'rb')
        text = file.read().split(b'\n')
        for i in range(0, len(text)):
            detector.feed(text[i])
            if detector.done: break
        detector.close()
        encoding = detector.result['encoding'] # can't always be relied upon
        if not encoding: raise Exception(f'{filename}: could not detect encoding, please specify manually')
        alert(f'{filename}: autodetected character encoding as {encoding.upper()}')
    columns = polars.read_csv(filename, encoding=encoding, n_rows=0).columns
    columns_new = disambiguate(columns)
    return polars.read_csv(filename, new_columns=columns_new, encoding=encoding, infer_schema=False)

def format(results: ArrowDataframe) -> None:
    cast(ArrowDataframe, polars.from_arrow(results)).write_csv(sys.__stdout__)
