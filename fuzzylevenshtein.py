import jellyfish
import jellyfish._jellyfish as py_jellyfish

def match(data1, data2, fields1, fields2, threshold, tick, weightings):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            values = zip(row1, row2)
            degree = 0
            for i, (value1, value2) in enumerate(values):
                maximum = float(max(len(value1), len(value2)))
                distance = damerau_levenshtein_distance(value1, value2)
                degree += (1 - distance / maximum) * weightings[i]
            if degree > threshold: matches.append((i1, i2, degree))
            if tick: tick()
    return matches


def damerau_levenshtein_distance(a, b):
    try:
        return jellyfish.damerau_levenshtein_distance(a, b)
    except ValueError: # c implementation can't deal with unicode, fall back to (slower) python
        return py_jellyfish.damerau_levenshtein_distance(a, b)
