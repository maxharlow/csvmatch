import jellyfish
import jellyfish._jellyfish as py_jellyfish

def match(value1, value2):
    maximum = float(max(len(value1), len(value2)))
    distance = damerau_levenshtein_distance(value1, value2)
    return 1 - distance / maximum

def damerau_levenshtein_distance(a, b):
    try:
        return jellyfish.damerau_levenshtein_distance(a, b)
    except ValueError: # c implementation can't deal with unicode, fall back to (slower) python
        return py_jellyfish.damerau_levenshtein_distance(a, b)
