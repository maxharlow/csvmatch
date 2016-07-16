import jellyfish._jellyfish as jellyfish # forces non-C version, which supports Unicode characters

def match(data1, data2, fields1, fields2):
    threshold = 0.4
    matches = []
    for data1key, data1values in data1.items():
        for data2key, data2values in data2.items():
            match = True
            for field1, field2 in zip(fields1, fields2):
                maximum = float(max(len(data1values[field1]), len(data2values[field2])))
                if jellyfish.damerau_levenshtein_distance(data1values[field1], data2values[field2]) / maximum > threshold: match = False
            if match: matches.append((data1key, data2key))
    return matches
