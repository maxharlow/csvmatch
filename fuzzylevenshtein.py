import jellyfish
import jellyfish._jellyfish as py_jellyfish

def match(data1, data2, fields1, fields2, threshold):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            match = False
            for field1, field2 in zip(fields1, fields2):
                maximum = float(max(len(row1[field1]), len(row2[field2])))
                distance = damerau_levenshtein_distance(row1[field1], row2[field2])
                degree = 1 - distance / maximum
                if degree > threshold: match = True
            if match: matches.append((i1, i2, degree))
    return matches

def damerau_levenshtein_distance(a, b):
    try:
        return jellyfish.damerau_levenshtein_distance(a, b)
    except ValueError: # c implementation can't deal with unicode, fall back to (slower) python
        return py_jellyfish.damerau_levenshtein_distance(a, b)
