import jellyfish

def match(data1, data2, fields1, fields2, threshold):
    matches = []
    for i1, row1 in enumerate(data1):
        for i2, row2 in enumerate(data2):
            match = False
            for field1, field2 in zip(fields1, fields2):
                degree = jellyfish.jaro_winkler(row1[field1], row2[field2])
                if degree > threshold: match = True
            if match: matches.append((i1, i2, degree))
    return matches
