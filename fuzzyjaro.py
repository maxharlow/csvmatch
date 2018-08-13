import jellyfish

def match(data1, data2, fields1, fields2, threshold, tick, weightings):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            values = zip(row1, row2)
            degree = 0
            for i, (value1, value2) in enumerate(values):
                degree += jellyfish.jaro_winkler(value1, value2) * weightings[i]
            if degree > threshold: matches.append((i1, i2, degree))
            if tick: tick()
    return matches
