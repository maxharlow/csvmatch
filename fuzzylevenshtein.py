import jellyfish._jellyfish as jellyfish # forces non-C version, which supports Unicode characters

def match(data1, data2, fields1, fields2):
    threshold = 0.6
    matches = []
    for data1key, data1values in data1.items():
        for data2key, data2values in data2.items():
            match = False
            for field1, field2 in zip(fields1, fields2):
                maximum = float(max(len(data1values[field1]), len(data2values[field2])))
                distance = jellyfish.damerau_levenshtein_distance(data1values[field1], data2values[field2])
                degree = 1 - distance / maximum
                if degree > threshold: match = True
            if match: matches.append((data1key, data2key, degree))
    return matches
