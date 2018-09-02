import jellyfish

def match(value1, value2):
    return jellyfish.jaro_winkler(value1, value2)
