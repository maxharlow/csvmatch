import doublemetaphone

def match(data1, data2, fields1, fields2):
    phonetic1 = [{key: doublemetaphone.doublemetaphone(value) for key, value in row.items()} for row in data1]
    phonetic2 = [{key: doublemetaphone.doublemetaphone(value) for key, value in row.items()} for row in data2]
    matches = []
    for i1, row1 in enumerate(phonetic1):
        for i2, row2 in enumerate(phonetic2):
            match = True
            for field1, field2 in zip(fields1, fields2):
                possibilities = [
                    row1.get(field1)[0] == row2.get(field2)[0],
                    row1.get(field1)[0] == row2.get(field2)[1],
                    row1.get(field1)[1] == row2.get(field2)[0],
                    row1.get(field1)[1] == row2.get(field2)[1] != ''
                ]
                if True not in possibilities: match = False
            if match: matches.append((i1, i2, 1))
    return matches
