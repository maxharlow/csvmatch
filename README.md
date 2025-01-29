CSV Match
=========

Find fuzzy matches between CSV files. Based on [Textmatch](https://github.com/maxharlow/textmatch).

Fuzzy matching is the art and science of connecting up bits of information that are written differently but represent the same _thing_ – such as a person or company.


Installing
----------

The best way to install is with `pipx`, which can be installed with Homebrew: `brew install pipx`. Then:

    pipx install csvmatch

If you get an error installing the most likely cause is an unsupported version of Python being used. You can find out which Python version is required [in this file](https://github.com/maxharlow/csvmatch/blob/master/pyproject.toml) then specify that version, eg:

    pipx install --python 3.x --fetch-missing-python csvmatch

If it installs without problems but you get a 'command not found' error when you run it, try:

    pipx ensurepath


Getting started
---------------

The best way to approach fuzzy matching with CSV Match is to start with an exact match. From there, you can incrementally improve the results by telling CSV Match about relevant information that should be taken into account and irrelevant information that should be disregarded. Experiment with different approaches. It is helpful to know what the data looks like, and how it has been collected.

The input files can be in CSV or Parquet format. The output results will be a CSV file.

<details>
  <summary>Example</summary>

  **`data1.csv`**:
  | name              | place    | codename  |
  |-------------------|----------|-----------|
  | Sam Collins       | Vietnam  | none      |
  | Roy Bland         | London   | Soldier   |
  | George Smiley     | London   | Beggerman |
  | Bill Haydon       | London   | Tailor    |
  | Perçy Allélíne    | London   | Tinker    |
  | Kretzschmar       | Hamburg  | none      |
  | Oliver Lacon      | London   | none      |
  | Jim Prideaux      | Slovakia | none      |
  | Peter Guillam Esq | Brixton  | none      |
  | Toby Esterhase    | Vienna   | Poorman   |
  | Connie Sachs      | Oxford   | none      |

  **`data2.csv`**:
  | Person Name                | Location       |
  |----------------------------|----------------|
  | Maria Andreyevna Ostrakova | Russia         |
  | Konny Saks                 | Oxford         |
  | Tony Esterhase             | Vienna         |
  | Peter Guillam              | Brixton        |
  | Mr Jim Prideaux            | Czech Republic |
  | Lacon Oliver               | Cambridge      |
  | Claus Kretzschmar          | Hamburg        |
  | Richard Bland              | London         |
  | Roy Rodgers                | Romania        |
  | Percy Alleline             | London         |
  | Bill-Haydon                | London         |
  | George SMILEY              | London         |
  | Roy Bland                  | UK             |
  | Sam Collins                | Vietnam        |

  To run an exact match on the **name** column from the first file against **Person Name** from the second:

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        > matches.csv

  The resulting matches include the two names which are written exactly the same:

  | name        | place   | codename | Person Name | Location |
  |-------------|---------|----------|-------------|----------|
  | Roy Bland   | London  | Soldier  | Roy Bland   | UK       |
  | Sam Collins | Vietnam | none     | Sam Collins | Vietnam  |

</details>


Matches are _many-to-many_, ie. it is possible for one row in the first file to match several rows in the second, and vice-versa.

> [!TIP]
> There is a tradeoff between false negatives and false positives – it is often better to have some incorrect matches in your results that can be manually checked afterwards than to have correct matches missing.


Usage
-----

CSV Match only requires two arguments, the first file followed by the second. All others are optional, described below:

### Fields

The `fields1` and `fields2` arguments accept one or more column names that should be used for the match. If the column name has a space it should be wrapped in quotes. These should be in the same order for both files – the first column specified for the first file will be compared against the first column specified for the second file, and so on. Defaults to comparing all columns. This flag can be specified multiple times for [blocking](#blocking).

<details>
  <summary>Example</summary>

  To match on the **name** and **place** columns from the first file against **Person Name** and **Location** from the second:

    $ csvmatch \
      data1.csv \
      data2.csv \
      --fields1 name place \
      --fields2 'Person Name' Location \
      > matches.csv

  The resulting matches include the single name-place pair which is the same in both files:

  | name        | place   | codename | Person Name | Location |
  |-------------|---------|----------|-------------|----------|
  | Sam Collins | Vietnam | none     | Sam Collins | Vietnam  |
</details>


### Ignorance

The `ignores` argument accepts one or more characteristics which should be disregarded for two records to be considered a match. This flag can be specified multiple times for [blocking](#blocking).

Combining different forms of ignorance can be quite powerful. The order in which you specify them is not significant.

**`case`** ignores how text is capitalised.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore case \
        > matches.csv

  The resulting matches include George Smiley, whose surname is in all-capitals in the second file:

  | name          | place   | codename  | Person Name   | Location |
  |---------------|---------|-----------|---------------|----------|
  | George Smiley | London  | Beggerman | George SMILEY | London   |
  | Roy Bland     | London  | Soldier   | Roy Bland     | UK       |
  | Sam Collins   | Vietnam | none      | Sam Collins   | Vietnam  |
</details>

**`nonalpha`** ignores anything that isn't a number or a letter.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore nonalpha \
        > matches.csv

  The resulting matches include Bill Haydon, whose name is written with a hypen in the second file:

  | name        | place   | codename | Person Name | Location |
  |-------------|---------|----------|-------------|----------|
  | Bill Haydon | London  | Tailor   | Bill-Haydon | London   |
  | Roy Bland   | London  | Soldier  | Roy Bland   | UK       |
  | Sam Collins | Vietnam | none     | Sam Collins | Vietnam  |
</details>

**`nonlatin`** ignores non-Latin characters – so `Jérôme` will match `Jerome`, `Weiß` will match `Weiss`, and `Пушкин` will match `Pushkin`. The further the script is from the Latin alphabet, the less accurate this transliteration will be.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore nonlatin \
        > matches.csv

  The resulting matches include Percy Alleline, whose name is written with several diacritics in the first file:

  | name             | place   | codename | Person Name    | Location |
  |------------------|---------|----------|----------------|----------|
  | Perçy Allélíne   | London  | Tinker   | Percy Alleline | London   |
  | Roy Bland        | London  | Soldier  | Roy Bland      | UK       |
  | Sam Collins      | Vietnam | none     | Sam Collins    | Vietnam  |
</details>

**`words-leading`** ignores all words except the last. This is useful for matching on surnames only.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore words-leading \
        > matches.csv

  The resulting matches include Toby and Tony Esterhase, Jim Prideaux and Mr Jim Prideaux, Kretzschmar and Claus Kretzschmar, as well as Roy and Richard Bland:

  | name           |  place   | codename | Person Name       | Location       |
  |----------------|----------|----------|-------------------|----------------|
  | Toby Esterhase | Vienna   | Poorman  | Tony Esterhase    | Vienna         |
  | Jim Prideaux   | Slovakia | none     | Mr Jim Prideaux   | Czech Republic |
  | Kretzschmar    | Hamburg  | none     | Claus Kretzschmar | Hamburg        |
  | Roy Bland      | London   | Soldier  | Richard Bland     | London         |
  | Roy Bland      | London   | Soldier  | Roy Bland         | UK             |
  | Sam Collins    | Vietnam  | none     | Sam Collins       | Vietnam        |
</details>

**`words-tailing`** ignore all words except the first.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore words-tailing \
        > matches.csv

  The resulting matches include Peter Guillam Esq and Peter Guillam, Roy Bland and Roy Rodgers, as well as the two capitalisations of George Smiley:

  | name              | place   | codename  | Person Name   | Location |
  |-------------------|---------|-----------|---------------|----------|
  | Peter Guillam Esq | Brixton | none      | Peter Guillam | Brixton  |
  | Roy Bland         | London  | Soldier   | Roy Rodgers   | Romania  |
  | George Smiley     | London  | Beggerman | George SMILEY | London   |
  | Roy Bland         | London  | Soldier   | Roy Bland     | UK       |
  | Sam Collins       | Vietnam | none      | Sam Collins   | Vietnam  |
</details>

**`words-order`** ignores the order in which the words are given. This is useful for matching names given surname-first with those given forename-first.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore words-order \
        > matches.csv

  The resulting matches include Oliver Lacon, whose name is written surname-first in the second file:

  | name         | place   | codename | Person Name  | Location  |
  |--------------|---------|----------|--------------|-----------|
  | Oliver Lacon | London  | none     | Lacon Oliver | Cambridge |
  | Roy Bland    | London  | Soldier  | Roy Bland    | UK        |
  | Sam Collins  | Vietnam | none     | Sam Collins  | Vietnam   |
</details>

**`titles`** ignores common English name prefixes such as Mr and Ms. There is a full list of these titles [here](https://github.com/maxharlow/textmatch/blob/main/src/textmatch/ignored-titles.txt).

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore titles \
        > matches.csv

  The resulting matches include Jim Prideaux, who has the title 'Mr' in the second file:

  | name         | place    | codename | Person Name     | Location       |
  |--------------|----------|----------|-----------------|----------------|
  | Jim Prideaux | Slovakia | none     | Mr Jim Prideaux | Czech Republic |
  | Roy Bland    | London   | Soldier  | Roy Bland       | UK             |
  | Sam Collins  | Vietnam  | none     | Sam Collins     | Vietnam        |
</details>

**`regex`** ignores terms specific to your data using a given regular expression. This is specified inline: `regex=EXPRESSION`.

<details>
  <summary>Example</summary>

  To use the regular expression ` Esq$` to ignore the word 'Esq' where it appear at the end of a value:

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore 'regex= Esq$' \
        > matches.csv

The resulting matches include Peter Guillam, who has the name suffix 'Esq' in the first file:

  | name              | place   | codename | Person Name   | Location |
  |-------------------|---------|----------|---------------|----------|
  | Peter Guillam Esq | Brixton | none     | Peter Guillam | Brixton  |
  | Roy Bland         | London  | Soldier  | Roy Bland     | UK       |
  | Sam Collins       | Vietnam | none     | Sam Collins   | Vietnam  |
</details>

### Methods & thresholds

The `methods` argument accepts one or more methods. This lets you specify the algorithm which is used to do the matching. Multiple methods are used for [blocking](#blocking).

There are three different categories of method:

* _Compared_ methods work by comparing every row from the first file with every row from the second, producing a number that represents the degree of the match. This means the amount of time required to run a match grows exponentially with the size of the input files. However, they are still useful for larger matches when using [blocking](#blocking).
* _Applied_ methods transform text into a different representation before they are matched up. These methods are quicker than compared ones, though no meaningful matching degree number is generated – either they match or they don't.
* _Custom_ methods have their own individual approach. CSV Match only has one, [Bilenko](#bilenko). It generates a matching degree number.

For those matching methods that generate a matching degree number there is then a threshold filter for any two records to be considered to be a match – you can adjust this with the `--threshold` argument, which accepts one or more numbers between 0.0 and 1.0, defaulting to 0.6. Multiple thresholds are also used for [blocking](#blocking).

You can also include the matching degree number as a column by specifying it in the [outputs](#outputs).

> [!WARNING]
> When working with names of people, exact matches, even when other pieces of information such as birthdays are included, are not a guarantee that the two names actually refer to the same human. Furthermore, the chance of a mismatch is unintuitively high – as illustrated by [the birthday paradox](https://pudding.cool/2018/04/birthday-paradox/).

**`literal`** is the default – it matches strings exactly, after ignored characteristics have been taken into account.

**`levenshtein`** Uses the [Damerau-Levenshtein](https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance) string distance metric that counts the number of changes that would have to be made to transform one string into another. Performs compared matching. Where two strings are of different lengths the longer string is used as the denominator for the threshold filter. Good at picking up typos and other small differences in spelling.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --method levenshtein \
        > matches.csv

  The resulting matches include various names with small typographical differences, though the most emblematic of this matching method would be Toby and Tony Esterhase:

  | name              | place    | codename  | Person Name       | Location       |
  |-------------------|----------|-----------|-------------------|----------------|
  | Sam Collins       | Vietnam  | none      | Sam Collins       | Vietnam        |
  | Roy Bland         | London   | Soldier   | Roy Bland         | UK             |
  | George Smiley     | London   | Beggerman | George SMILEY     | London         |
  | Bill Haydon       | London   | Tailor    | Bill-Haydon       | London         |
  | Perçy Allélíne    | London   | Tinker    | Percy Alleline    | London         |
  | Kretzschmar       | Hamburg  | none      | Claus Kretzschmar | Hamburg        |
  | Jim Prideaux      | Slovakia | none      | Mr Jim Prideaux   | Czech Republic |
  | Peter Guillam Esq | Brixton  | none      | Peter Guillam     | Brixton        |
  | Toby Esterhase    | Vienna   | Poorman   | Tony Esterhase    | Vienna         |
</details>

**`jaro`** uses the [Jaro-Winkler](https://en.wikipedia.org/wiki/Jaro–Winkler_distance) string distance metric that counts characters in common, though it considers differences near the start of the string to be more significant than differences near the end. Performs compared matching. It tends to work better than Levenshtein for shorter strings of text.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --method jaro \
        > matches.csv

  The resulting matches includes many more matches than `levenshtein`, though also many more false positives:

  | name              | place    | codename  | Person Name       | Location       |
  |-------------------|----------|-----------|-------------------|----------------|
  | Sam Collins       | Vietnam  | none      | Percy Alleline    | London         |
  | Sam Collins       | Vietnam  | none      | Sam Collins       | Vietnam        |
  | Roy Bland         | London   | Soldier   | Richard Bland     | London         |
  | Roy Bland         | London   | Soldier   | Roy Rodgers       | Romania        |
  | Roy Bland         | London   | Soldier   | Bill-Haydon       | London         |
  | Roy Bland         | London   | Soldier   | Roy Bland         | UK             |
  | George Smiley     | London   | Beggerman | George SMILEY     | London         |
  | Bill Haydon       | London   | Tailor    | Bill-Haydon       | London         |
  | Bill Haydon       | London   | Tailor    | Roy Bland         | UK             |
  | Perçy Allélíne    | London   | Tinker    | Peter Guillam     | Brixton        |
  | Perçy Allélíne    | London   | Tinker    | Percy Alleline    | London         |
  | Kretzschmar       | Hamburg  | none      | Claus Kretzschmar | Hamburg        |
  | Jim Prideaux      | Slovakia | none      | Mr Jim Prideaux   | Czech Republic |
  | Peter Guillam Esq | Brixton  | none      | Peter Guillam     | Brixton        |
  | Toby Esterhase    | Vienna   | Poorman   | Tony Esterhase    | Vienna         |
  | Toby Esterhase    | Vienna   | Poorman   | Roy Rodgers       | Romania        |
  | Connie Sachs      | Oxford   | none      | Konny Saks        | Oxford         |
</details>

**`metaphone`** uses the [Double Metaphone](https://en.wikipedia.org/wiki/Metaphone#Double_Metaphone) phonetic encoding algorithm to convert words into a representation of how they are pronounced. Performs applied matching. Tends to work better for data which has been transcribed or transliterated.

<details>
  <summary>Example</summary>

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --method metaphone \
        > matches.csv

  The resulting matches includes those with nonalphanumeric differences, as well as Connie Sachs and Konny Saks, names written quite differently that would be pronounced the same:

  | name          | place   | codename  | Person Name   | Location |
  |---------------|---------|-----------|---------------|----------|
  | Connie Sachs  | Oxford  | none      | Konny Saks    | Oxford   |
  | Roy Bland     | London  | Soldier   | Roy Bland     | UK       |
  | George Smiley | London  | Beggerman | George SMILEY | London   |
  | Sam Collins   | Vietnam | none      | Sam Collins   | Vietnam  |
  | Bill Haydon   | London  | Tailor    | Bill-Haydon   | London   |
</details>

**`bilenko`** uses [Dedupe](https://github.com/dedupeio/dedupe), a library built by Forest Gregg and Derek Eder based on the work of Mikhail Bilenko that will ask you to train it by asking whether different pairs of records should match. The information you give it is then extrapolated to match up the rest of the file. The more examples you give it, the better the results will be. At minimum, try to provide 10 positive matches and 10 negative matches. Performs custom matching.

### Blocking

Blocking is the approach of performing multiple matches, with subsequent matches only applying to the subset of matches resulting from the previous match. This can make matches both quicker and more precise. This is an advanced topic, and can be ignored if you are happy with the quality of matches and are dealing with smaller files.

In a 'regular' match, you are really just matching using a single block. Each block is defined by: a list of fields for each file, a list of ignores, a method, and a threshold. To perform a blocked match CSV Match needs to know each of these things for each block. You specify these through list arguments, or through outer lists for those arguments where the block requires a list itself. If you specify one of these things less than the total number of blocks – such as if you had two blocks, but specified the threshold once – that value will then be used for all subsequent blocks.

<details>
  <summary>Example</summary>

  To specify a first block that does a case-insensitive literal match on surnames, then a second block performing a Levenshtein match on forenames:

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --ignore case words-leading \
        --ignore words-tailing \
        --method literal levenshtein \
        > matches.csv

  |     name      |  place  | codename  |    Person Name    | Location |
  |---------------|---------|-----------|-------------------|----------|
  | Kretzschmar   | Hamburg | none      | Claus Kretzschmar | Hamburg  |
  | George Smiley | London  | Beggerman | George SMILEY     | London   |
  | Roy Bland     | London  | Soldier   | Roy Bland         | UK       |
  | Sam Collins   | Vietnam | none      | Sam Collins       | Vietnam  |
</details>

### Outputs

The `output` argument accepts a list of column names which should appear in the output, each prefixed with a number and a dot indicating which file that field is from. They are case-sensitive, and can be in any order you desire. It defaults to all columns in the first file, followed by all columns in the second.

There are some special column definitions: `1*` and `2*` expand into all columns from the first and second files respectively, and `degree` will add a column with the matching degree number.

<details>
  <summary>Example</summary>

  To include every column from the second file, followed by the **codename** column from the first, followed by the matching degree:

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --method levenshtein \
        --output '2*' 1.codename degree \
        > matches.csv

  | Person Name       | Location       | codename  | degree     |
  |-------------------|----------------|-----------|------------|
  | Sam Collins       | Vietnam        | none      | 1.0        |
  | Roy Bland         | UK             | Soldier   | 1.0        |
  | George SMILEY     | London         | Beggerman | 0.61538464 |
  | Bill-Haydon       | London         | Tailor    | 0.90909094 |
  | Percy Alleline    | London         | Tinker    | 0.78571427 |
  | Claus Kretzschmar | Hamburg        | none      | 0.64705884 |
  | Mr Jim Prideaux   | Czech Republic | none      | 0.8        |
  | Peter Guillam     | Brixton        | none      | 0.7647059  |
  | Tony Esterhase    | Vienna         | Poorman   | 0.9285714  |
</details>

### Join types

The `join` argument takes a string that indicates what other nonmatching records should be included in the output. A `left-outer` join will return everything from the first file, whether there was a match or not, a `right-outer` to do the same but for the second file, and a `full-outer` to return everything from both files. Where two rows didn't match the values will be blank. Defaults to an `inner` join, where only successful matches are returned.

<details>
  <summary>Example</summary>

  To include all rows from the first file, but only those that match from the second:

    $ csvmatch \
        data1.csv \
        data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --join left-outer \
        > matches.csv

  | name              | place    | codename  | Person Name | Location |
  |-------------------|----------|-----------|-------------|----------|
  | Roy Bland         | London   | Soldier   | Roy Bland   | UK       |
  | Sam Collins       | Vietnam  | none      | Sam Collins | Vietnam  |
  | George Smiley     | London   | Beggerman |             |          |
  | Bill Haydon       | London   | Tailor    |             |          |
  | Perçy Allélíne    | London   | Tinker    |             |          |
  | Kretzschmar       | Hamburg  | none      |             |          |
  | Oliver Lacon      | London   | none      |             |          |
  | Jim Prideaux      | Slovakia | none      |             |          |
  | Peter Guillam Esq | Brixton  | none      |             |          |
  | Toby Esterhase    | Vienna   | Poorman   |             |          |
  | Connie Sachs      | Oxford   | none      |             |          |
</details>
