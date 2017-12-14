import doublemetaphone

def match(data1, data2, fields1, fields2, threshold): # threshold is unused
    phonetic1 = [[doublemetaphone.doublemetaphone(value) for value in row] for row in data1]
    phonetic2 = [[doublemetaphone.doublemetaphone(value) for value in row] for row in data2]
    matches = []
    for i1, row1 in enumerate(phonetic1):
        for i2, row2 in enumerate(phonetic2):
            match = True
            for metaphone1, metaphone2 in zip(row1, row2):
                possibilities = [
                    metaphone1[0] == metaphone2[0],
                    metaphone1[0] == metaphone2[1],
                    metaphone1[1] == metaphone2[0],
                    metaphone1[1] == metaphone2[1] != ''
                ]
                if True not in possibilities: match = False
            if match: matches.append((i1, i2, 1))
    return matches
