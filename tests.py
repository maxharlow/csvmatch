import csvmatch

def test_simple():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway' },
        { 'person': 'William Shakespeare' }
    ]
    results, _ = csvmatch.run(data1, data2)
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'William Shakespeare' }
    ]

def test_fields():
    data1 = [
        { 'name': 'William Shakespeare', 'born': '1564' },
        { 'name': 'Christopher Marlowe', 'born': '1583' }
    ]
    data2 = [
        { 'person': 'Christopher Marlowe', 'birth': 'unknown' },
        { 'person': 'William Shakespeare', 'birth': '1564' }
    ]
    results, _ = csvmatch.run(data1, data2)
    assert results == [
        { 'name': 'William Shakespeare', 'born': '1564', 'person': 'William Shakespeare', 'birth': '1564' }
    ]

def test_multiple():
    data1 = [
        { 'name': 'Anne Hathaway' },
        { 'name': 'Anne Hathaway' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway' },
        { 'person': 'Christopher Marlowe' },
        { 'person': 'Christopher Marlowe' }
    ]
    results, _ = csvmatch.run(data1, data2)
    assert results == [
        { 'name': 'Anne Hathaway', 'person': 'Anne Hathaway' },
        { 'name': 'Anne Hathaway', 'person': 'Anne Hathaway' },
        { 'name': 'Christopher Marlowe', 'person': 'Christopher Marlowe' },
        { 'name': 'Christopher Marlowe', 'person': 'Christopher Marlowe' }
    ]

def test_coalesce():
    data1 = [
        { 'name': 'Anne Hathaway' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe' }
    ]
    results, _ = csvmatch.run(data1, data2)
    assert results == [
        { 'name': 'Christopher Marlowe' } # this is not really desirable, but here we are
    ]

def test_fields():
    data1 = [
        { 'name': 'William Shakespeare', 'born': '1564' },
        { 'name': 'Christopher Marlowe', 'born': '1564' }
    ]
    data2 = [
        { 'person': 'William Shakespeare', 'hometown': 'Stratford-upon-Avon' },
        { 'person': 'Anne Hathaway', 'hometown': 'Stratford-upon-Avon' }
    ]
    results, _ = csvmatch.run(data1, data2, fields1=['name'], fields2=['person'])
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'William Shakespeare' }
    ]

def test_ignore_case():
    data1 = [
        { 'name': 'Anne Hathaway' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'william shakespeare' },
        { 'person': 'christopher marlowe' }
    ]
    results, _ = csvmatch.run(data1, data2, ignore_case=True)
    assert results == [
        { 'name': 'Christopher Marlowe', 'person': 'christopher marlowe' }
    ]

def test_filter():
    data1 = [
        { 'name': 'ONE Anne Hathaway' },
        { 'name': 'TWO Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'THREE Christopher Marlowe' },
        { 'person': 'FOUR William Shakespeare' }
    ]
    results, _ = csvmatch.run(data1, data2, filter=['ONE', 'TWO', 'THREE', 'FOUR'])
    assert results == [
        { 'name': 'TWO Christopher Marlowe', 'person': 'THREE Christopher Marlowe' }
    ]

def test_filter_titles():
    data1 = [
        { 'name': 'Ms. Anne Hathaway' },
        { 'name': 'Mr. William Shakespeare' }
    ]
    data2 = [
        { 'person': 'Mr. Christopher Marlowe' },
        { 'person': 'Mrs. Anne Hathaway' }
    ]
    results, _ = csvmatch.run(data1, data2, filter_titles=True)
    assert results == [
        { 'name': 'Ms. Anne Hathaway', 'person': 'Mrs. Anne Hathaway' }
    ]

def test_as_latin():
    data1 = [
        { 'name': 'Charlotte Brontë' },
        { 'name': 'Gabriel García Márquez' }
    ]
    data2 = [
        { 'person': 'Gabriel Garcia Marquez' },
        { 'person': 'Leo Tolstoy' }
    ]
    results, _ = csvmatch.run(data1, data2, as_latin=True)
    assert results == [
        { 'name': 'Gabriel García Márquez', 'person': 'Gabriel Garcia Marquez' }
    ]

def test_ignore_nonalpha():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway!' },
        { 'person': 'William Shakespeare.' }
    ]
    results, _ = csvmatch.run(data1, data2, ignore_nonalpha=True)
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'William Shakespeare.' }
    ]

def test_sort_words():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Anne Hathaway' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway' },
        { 'person': 'Shakespeare William' }
    ]
    results, _ = csvmatch.run(data1, data2, sort_words=True)
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'Shakespeare William' },
        { 'name': 'Anne Hathaway', 'person': 'Anne Hathaway' }
    ]

def test_fuzzy_levenshtein():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Anne Hathaway' }
    ]
    data2 = [
        { 'person': 'Ann Athawei' },
        { 'person': 'Will Sheikhspere' }
    ]
    results, _ = csvmatch.run(data1, data2, algorithm='levenshtein')
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'Will Sheikhspere' },
        { 'name': 'Anne Hathaway', 'person': 'Ann Athawei' }
    ]

def test_fuzzy_metaphone():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Anne Hathaway' }
    ]
    data2 = [
        { 'person': 'Ann Athawei' },
        { 'person': 'Will Sheikhspere' }
    ]
    results, _ = csvmatch.run(data1, data2, algorithm='metaphone')
    assert results == [
        { 'name': 'Anne Hathaway', 'person': 'Ann Athawei' }
    ]

def test_output():
    data1 = [
        { 'name': 'William Shakespeare', 'born': '1564' },
        { 'name': 'Christopher Marlowe', 'born': '1583' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway', 'died': '1623' },
        { 'person': 'William Shakespeare', 'died': '1616' }
    ]
    results, _ = csvmatch.run(data1, data2, fields1=['name'], fields2=['person'], output=['1*', '2.died', 'degree'])
    assert results == [
        { 'name': 'William Shakespeare', 'born': '1564', 'died': '1616', 'degree': '1' }
    ]

def test_join_left_outer():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway' },
        { 'person': 'William Shakespeare' }
    ]
    results, _ = csvmatch.run(data1, data2, join='left-outer')
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe', 'person': '' }
    ]

def test_join_right_outer():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway' },
        { 'person': 'William Shakespeare' }
    ]
    results, _ = csvmatch.run(data1, data2, join='right-outer')
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'William Shakespeare' },
        { 'name': '', 'person': 'Anne Hathaway' }
    ]

def test_join_full_outer():
    data1 = [
        { 'name': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe' }
    ]
    data2 = [
        { 'person': 'Anne Hathaway' },
        { 'person': 'William Shakespeare' }
    ]
    results, _ = csvmatch.run(data1, data2, join='full-outer')
    assert results == [
        { 'name': 'William Shakespeare', 'person': 'William Shakespeare' },
        { 'name': 'Christopher Marlowe', 'person': '' },
        { 'name': '', 'person': 'Anne Hathaway' }
    ]
