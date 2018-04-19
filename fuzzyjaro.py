import jellyfish

def match(data1, data2, fields1, fields2, threshold, tick):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            match = False
            for value1, value2 in zip(row1, row2):
                degree = jellyfish.jaro_winkler(value1, value2)
                if degree > threshold: match = True
                if tick: tick()
            if match: matches.append((i1, i2, degree))
    return matches
