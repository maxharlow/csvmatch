import doublemetaphone

def match(value1, value2):
    value1metaphone_words = [doublemetaphone.doublemetaphone(word) for word in value1.split(' ')]
    value2metaphone_words = [doublemetaphone.doublemetaphone(word) for word in value2.split(' ')]
    value1metaphone = [' '.join(permutations) for permutations in zip(*value1metaphone_words)]
    value2metaphone = [' '.join(permutations) for permutations in zip(*value2metaphone_words)]
    possibilities = [
        value1metaphone[0] == value2metaphone[0],
        value1metaphone[0] == value2metaphone[1],
        value1metaphone[1] == value2metaphone[0],
        value1metaphone[1] == value2metaphone[1] != ''
    ]
    return 1.0 if True in possibilities else 0.0
