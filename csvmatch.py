import functools
import sys
import os
import io
import re
import csv
import unidecode

def run(
        data1,
        headers1,
        data2,
        headers2,
        fields1=None,
        fields2=None,
        ignore_case=False,
        ignore_nonalpha=False,
        ignore_nonlatin=False,
        ignore_order_words=False,
        ignore_order_letters=False,
        ignore_titles=False,
        ignore_custom=None,
        methods=['exact'],
        thresholds=[0.6],
        output=None,
        join='inner',
        ticker=None
    ):
    fields1 = fields1 if fields1 else headers1
    fields2 = fields2 if fields2 else headers2
    for field in fields1:
        if field not in headers1: raise Exception(field + ': field not found')
    for field in fields2:
        if field not in headers2: raise Exception(field + ': field not found')
    if len(fields1) != len(fields2):
        raise Exception('both files must have the same number of columns specified')
    extracted1 = extract(data1, headers1, fields1)
    extracted2 = extract(data2, headers2, fields2)
    processes = [
        (process_ignore_case, ignore_case),
        (process_ignore_custom(ignore_custom, ignore_case), ignore_custom),
        (process_ignore_nonlatin, ignore_nonlatin), # must be after custom in case it expects an accented character that would then be removed and prevent a match
        (process_ignore_titles(ignore_case), ignore_titles), # must be after nonlatin so characters are convered at this point (also as no titles include accented characters)
        (process_ignore_order_words, ignore_order_words), # must be after titles and custom so regex anchors work, and after nonlatin so words sorted in comparable orders
        (process_ignore_nonalpha, ignore_nonalpha), # must be after order words so there are still spaces
        (process_ignore_order_letters, ignore_order_letters) # must be after nonlatin so accented characters are in latin-equivalent order, and after case so that doesn't change the order
    ]
    processed1 = list(process(extracted1, processes))
    processed2 = list(process(extracted2, processes))
    tick = ticker('Matching', len(processed1) * len(processed2)) if ticker and 'bilenko' not in methods else None
    matcher = build(methods, thresholds, fields1, fields2, tick)
    matches = matcher(processed1, processed2)
    outputs = format(output, headers1, headers2, fields1, fields2)
    results = connect(join, data1, headers1, data2, headers2, list(matches), outputs)
    keys = [key for _, key in outputs]
    return results, keys

def extract(data, headers, fields):
    indexes = [headers.index(field) for field in fields]
    return ([row[i] for i in indexes] for row in data)

def process(data, processes):
    functions = [function for function, selected in processes if selected]
    processor = functools.reduce(lambda f1, f2: lambda x: f2(f1(x)), functions, lambda x: x)
    return (processor(row) for row in data)

def process_ignore_case(row):
    return [value.lower() for value in row]

def process_ignore_nonalpha(row):
    regex = re.compile('[\W_]+')
    return [regex.sub('', value) for value in row]

def process_ignore_nonlatin(row):
    return [unidecode.unidecode(value) for value in row]

def process_ignore_order_words(row):
    return [' '.join(sorted(value.split(' '))) for value in row]

def process_ignore_order_letters(row):
    return [''.join(sorted(value)) for value in row]

def process_ignore_custom(filters, ignore_case):
    if filters == None: return
    def filterer(row):
        regex = re.compile('(' + '|'.join(filters) + ')', re.IGNORECASE if ignore_case else 0)
        return [regex.sub('', value) for value in row]
    return filterer

def process_ignore_titles(ignore_case):
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'csvmatch-titles.txt.py')
    titles = [line[:-1] for line in io.open(filename)]
    return process_ignore_custom(titles, ignore_case)

def build(methods, thresholds, fields1, fields2, tick):
    if 'bilenko' in methods and len(methods) > 1:
        raise Exception('bilenko compares whole rows so cannot be combined with other methods')
    if methods[0] == 'bilenko':
        import fuzzybilenko
        return fuzzybilenko.setup(fields1, fields2, thresholds[0])
    matchers = []
    for i, (field1, field2) in enumerate(zip(fields1, fields2)):
        method = methods[i] if len(methods) >= i + 1 else methods[-1]
        threshold = thresholds[i] if len(thresholds) >= i + 1 else thresholds[-1]
        if threshold < 0 or threshold > 1:
            raise Exception('threshold must be between 0.0 and 1.0 (inclusive)')
        method_function = None
        if method == 'exact':
            method_function = lambda value1, value2: 1.0 if value1 == value2 else 0.0
        elif method == 'levenshtein':
            import fuzzylevenshtein
            method_function = fuzzylevenshtein.match
        elif method == 'jaro':
            import fuzzyjaro
            method_function = fuzzyjaro.match
        elif method == 'metaphone':
            import fuzzymetaphone
            method_function = fuzzymetaphone.match
        else:
            raise Exception(method + ': method does not exist')
        matchers.append({
            'method': method_function,
            'threshold': threshold
        })
    def executor(data1, data2):
        for i1, row1 in enumerate(data1):
            for i2, row2 in enumerate(data2):
                degrees = []
                for i, matcher in enumerate(matchers):
                    degree = matcher['method'](row1[i], row2[i])
                    if degree < matcher['threshold']: break
                    else: degrees.append(degree)
                if tick: tick()
                if len(degrees) == len(matchers):
                    degree = sum(degrees) / len(degrees)
                    yield (i1, i2, degree)
    return executor

def format(output, headers1, headers2, fields1, fields2):
    if len(headers1) != len(set(headers1)):
        raise Exception('first file has duplicate headers')
    if len(headers2) != len(set(headers2)):
        raise Exception('second file has duplicate headers')
    if output == None: # note that output defaults to fields, not headers
        return [('1', key) for key in fields1] + [('2', key) for key in fields2]
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

def connect(join, data1, headers1, data2, headers2, matches, outputs):
    if join.lower() not in ['inner', 'left-outer', 'right-outer', 'full-outer']:
        raise Exception(join + ': join type not known')
    results = []
    for match in matches:
        row = []
        for number, key in outputs:
            if number == '1':
                y = match[0]
                x = headers1.index(key)
                row.append(data1[y][x])
            elif number == '2':
                y = match[1]
                x = headers2.index(key)
                row.append(data2[y][x])
            elif number == '-':
                row.append(str(match[2]))
        results.append(row)
    if join.lower() == 'full-outer' or join.lower() == 'left-outer':
        matches1 = [match[0] for match in matches]
        for i, row1 in enumerate(data1):
            if i in matches1: continue
            row = []
            for number, key in outputs:
                if number == '1':
                    x = headers1.index(key)
                    row.append(row1[x])
                elif number == '2':
                    row.append('')
                elif number == '-':
                    row.append('')
            results.append(row)
    if join.lower() == 'full-outer' or join.lower() == 'right-outer':
        matches2 = [match[1] for match in matches]
        for i, row2 in enumerate(data2):
            if i in matches2: continue
            row = []
            for number, key in outputs:
                if number == '1':
                    row.append('')
                elif number == '2':
                    x = headers2.index(key)
                    row.append(row2[x])
                elif number == '-':
                    row.append('')
            results.append(row)
    return results
