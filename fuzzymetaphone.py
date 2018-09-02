import doublemetaphone

def match(value1, value2):
    value1metaphone = doublemetaphone.doublemetaphone(value1)
    value2metaphone = doublemetaphone.doublemetaphone(value2)
    possibilities = [
        value1metaphone[0] == value2metaphone[0],
        value1metaphone[0] == value2metaphone[1],
        value1metaphone[1] == value2metaphone[0],
        value1metaphone[1] == value2metaphone[1] != ''
    ]
    return 1.0 if True in possibilities else 0.0
