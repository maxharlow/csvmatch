import jellyfish

def match(value1, value2):
    maximum = float(max(len(value1), len(value2)))
    distance = jellyfish.damerau_levenshtein_distance(value1, value2)
    return 1 - distance / maximum
