import sys
import os
import io
import re
import csv
import unidecode

def run(
        data1,
        data2,
        fields1=None,
        fields2=None,
        ignore_case=False,
        filter_titles=False,
        filter=None,
        as_latin=False,
        ignore_nonalpha=False,
        sort_words=False,
        algorithm=None,
        threshold=0.6,
        output=None,
        join='inner'
    ):
    headers1 = data1[0].keys()
    headers2 = data2[0].keys()
    fields1 = fields1 if fields1 else headers1
    fields2 = fields2 if fields2 else headers2
    for field in fields1:
        if field not in headers1: raise Exception(field + ': field not found')
    for field in fields2:
        if field not in headers2: raise Exception(field + ': field not found')
    if len(fields1) != len(fields2):
        raise Exception('both files must have the same number of columns specified')
    if threshold < 0 or threshold > 1:
        raise Exception('threshold must be between 0.0 and 1.0')
    processes = [
        (process_ignore_case, ignore_case),
        (process_filter_titles(ignore_case), filter_titles),
        (process_filter(filter, ignore_case), filter),
        (process_as_latin, as_latin),
        (process_ignore_nonalpha, ignore_nonalpha),
        (process_sort_words, sort_words)
    ]
    processed1 = process(data1, processes)
    processed2 = process(data2, processes)
    matches = matcher(algorithm)(processed1, processed2, fields1, fields2, threshold)
    outputs = format(output, headers1, headers2, fields1, fields2)
    results, keys = connect(join, data1, data2, outputs, matches)
    return results, keys

def process(data, processes):
    processed = list(data) # a copy
    for process, selected in processes:
        processed = process(processed) if selected else processed
    return processed

def process_ignore_case(data):
    return [{key: value.lower() for key, value in row.items()} for row in data]

def process_filter(filters, ignore_case):
    if filters == None: return
    def filterer(data):
        regex = re.compile('(' + '|'.join(filters) + ')', re.IGNORECASE if ignore_case else 0)
        return [{key: regex.sub('', value) for key, value in row.items()} for row in data]
    return filterer

def process_filter_titles(ignore_case):
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'csvmatch-titles.txt.py')
    titles = [line[:-1] for line in io.open(filename)]
    return process_filter(titles, ignore_case)

def process_as_latin(data):
    return [{key: unidecode.unidecode(value) for key, value in row.items()} for row in data]

def process_ignore_nonalpha(data):
    regex = re.compile('[^A-Za-z0-9 ]') # does not take into account non-latin alphabet
    return [{key: regex.sub('', value) for key, value in row.items()} for row in data]

def process_sort_words(data):
    return [{key: ' '.join(sorted(value.split(' '))) for key, value in row.items()} for row in data]

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

def match(data1, data2, fields1, fields2, threshold):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            match = True
            for field1, field2 in zip(fields1, fields2):
                if row1[field1] != row2[field2]: match = False
            if match: matches.append((i1, i2, 1))
    return matches

def format(output, headers1, headers2, fields1, fields2):
    if output == None: return [('1', key) for key in fields1] + [('2', key) for key in fields2]
    outputs = []
    for definition in output:
        if re.match('^[1|2]\..*', definition): # standard header definitions
            header = definition.split('.', 1)
            if (header[0] == '1' and header[1] not in headers1) or (header[0] == '2' and header[1] not in headers2):
                raise Exception(header[1] + ': field not found in file ' + header[0])
            outputs.append((header[0], header[1]))
        elif re.match('^[1|2]\*$', definition): # expand 1* and 2* to all columns from that file
            number = definition.split('*')[0]
            if   number == '1': outputs = outputs + [('1', key) for key in headers1]
            elif number == '2': outputs = outputs + [('2', key) for key in headers2]
        elif definition == 'degree': # the matching degree
            outputs.append(('-', 'degree'))
        else: raise Exception('output format must be the file number, followed by a dot, followed by the name of the column')
    return outputs

def connect(join, data1, data2, outputs, matches):
    if join.lower() not in ['inner', 'left-outer', 'right-outer', 'full-outer']:
        raise Exception(join + ': join type not known')
    results = []
    for match in matches:
        row = {}
        for number, key in outputs:
            if   number == '1': row[key] = data1[match[0]][key]
            elif number == '2': row[key] = data2[match[1]][key]
            elif number == '-': row[key] = str(match[2])
        results.append(row)
    if join.lower() == 'full-outer' or join.lower() == 'left-outer':
        matches1 = [match[0] for match in matches]
        for i, row1 in enumerate(data1):
            if i not in matches1:
                row = {}
                for number, key in outputs:
                    if   number == '1': row[key] = row1[key]
                    elif number == '2': row[key] = ''
                    elif number == '-': row[key] = ''
                results.append(row)
    if join.lower() == 'full-outer' or join.lower() == 'right-outer':
        matches2 = [match[1] for match in matches]
        for i, row2 in enumerate(data2):
            if i not in matches2:
                row = {}
                for number, key in outputs:
                    if   number == '1': row[key] = ''
                    elif number == '2': row[key] = row2[key]
                    elif number == '-': row[key] = ''
                results.append(row)
    keys = [key for _, key in outputs]
    return results, keys
