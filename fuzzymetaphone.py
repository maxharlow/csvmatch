import metaphone

def match(data1, data2, fields1, fields2):
    data1phonetic = {key: {field: metaphone.doublemetaphone(data1[key][field]) for field in data1[key]} for key in data1}
    data2phonetic = {key: {field: metaphone.doublemetaphone(data2[key][field]) for field in data2[key]} for key in data2}
    matches = []
    for data1key, data1values in data1phonetic.items():
        for data2key, data2values in data2phonetic.items():
            match = True
            for field1, field2 in zip(fields1, fields2):
                possibilities = [
                    data1values.get(field1)[0] == data2values.get(field2)[0],
                    data1values.get(field1)[0] == data2values.get(field2)[1],
                    data1values.get(field1)[1] == data2values.get(field2)[0],
                    data1values.get(field1)[1] == data2values.get(field2)[1] != ''
                ]
                if True not in possibilities: match = False
            if match: matches.append((data1key, data2key))
    return matches
