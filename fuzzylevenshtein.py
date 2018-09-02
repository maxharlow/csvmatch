import jellyfish
import jellyfish._jellyfish as py_jellyfish

def match(data1, data2, fields1, fields2, threshold, tick):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            degrees = []
            for value1, value2 in zip(row1, row2):
                maximum = float(max(len(value1), len(value2)))
                distance = damerau_levenshtein_distance(value1, value2)
                degrees.append(1 - distance / maximum)
            degree = sum(degrees) / len(degrees)
            if degree > threshold:
                matches.append((i1, i2, degree))
            if tick: tick()
    return matches

def damerau_levenshtein_distance(a, b):
    try:
        return jellyfish.damerau_levenshtein_distance(a, b)
    except ValueError: # c implementation can't deal with unicode, fall back to (slower) python
        return py_jellyfish.damerau_levenshtein_distance(a, b)
