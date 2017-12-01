import sys
import dedupe
import colorama

def match(data1, data2, fields1, fields2, threshold): # threshold not used, as is automatically calculated
    input1 = {i: row for i, row in enumerate(data1)}
    input2 = {i: row for i, row in enumerate(remap(data2, fields1, fields2))}
    fields = [{'field': field, 'type': 'String'} for field in fields1]
    linker = dedupe.RecordLink(fields)
    linker.sample(input1, input2, sample_size=1500)
    while True:
        labelling(linker)
        try:
            linker.train()
            break
        except ValueError: sys.stderr.write('\nYou need to do more training.\n')
    threshold = linker.threshold(input1, input2, recall_weight=1)
    pairs = linker.match(input1, input2, threshold)
    matches = []
    for pair in pairs:
        matches.append((pair[0][0], pair[0][1], pair[1]))
    return matches

def remap(data, fields_new, fields_old): # converts data to use a new set of fields (dedupe insists they should be the same)
    data_remapped = []
    for i, row in enumerate(data):
        item = {}
        for field_new, field_old in zip(fields_new, fields_old):
            item[field_new] = row[field_old]
        data_remapped.append(item)
    return data_remapped

def labelling(linker):
    colorama.init()
    sys.stderr.write('\n' + colorama.Style.BRIGHT + colorama.Fore.BLUE + 'Answer questions as follows:\n y - yes\n n - no\n s - skip\n f - finished' + colorama.Style.RESET_ALL + '\n')
    labels = { 'distinct': [], 'match': [] }
    finished = False
    while not finished:
        for pair in linker.uncertainPairs():
            if pair[0] == pair[1]: # if they are exactly the same, presume a match
                labels['match'].append(pair)
                continue
            for record in pair:
                sys.stderr.write('\n')
                for field in set(field.field for field in linker.data_model.primary_fields):
                    sys.stderr.write(colorama.Style.BRIGHT + field + ': ' + colorama.Style.RESET_ALL + record[field] + '\n')
            sys.stderr.write('\n')
            responded = False
            while not responded:
                sys.stderr.write(colorama.Style.BRIGHT + colorama.Fore.BLUE + 'Do these records refer to the same thing? [y/n/s/f]' + colorama.Style.RESET_ALL + ' ')
                response = input() if sys.version_info >= (3, 0) else raw_input()
                responded = True
                if   response == 'y': labels['match'].append(pair)
                elif response == 'n': labels['distinct'].append(pair)
                elif response == 's': continue
                elif response == 'f': finished = True
                else: responded = False
    linker.markPairs(labels)
