CSV Match
=========

Find (fuzzy) matches between two CSV files in the terminal.

Tested on Python 2.7 and 3.5.


Installing
----------

    pip install csvmatch


Usage
-----

Say you have one CSV file such as:

```
name
George Smiley
Percy Alleline
Roy Bland
Toby Esterhase
Peter Guillam
Bill Haydon
Oliver Lacon
Jim Prideaux
Connie Sachs
```

And another such as:

```
name
Maria Andreyevna Ostrakova
Otto Leipzig
George SMILEY
Peter Guillam
Konny Saks
Saul Enderby
Sam Collins
Tony Esterhase
Claus Kretzschmar
```

You can then find the matches:

```bash
$ csvmatch data1.csv data2.csv

name,name
Peter Guillam,Peter Guillam
```

By default this is case-sensitive. We can make it case insensitive with `-i`:

```bash
$ csvmatch data1.csv data2.csv -i

name,name
George Smiley,George SMILEY
Peter Guillam,Peter Guillam
```

By default, all columns are used to compare rows. Specific columns can be also be given to be compared -- these should be in the same order for both files. Column headers with a space should be enclosed in quotes.

```bash
$ csvmatch dataA.csv dataB.csv \
    --fields1 name address \
    --fields2 'Person Name' Address \
	> results.csv
```

(This example also uses output redirection to save the results to a file.)

Either file can also be piped in using `-` as a placeholder:

```bash
$ cat data1.csv | csvmatch - data2.csv
```

CSV Match also supports fuzzy matching.

### Fuzzy matching: Bilenko

The default fuzzy mode makes use of the [Dedupe library] (https://github.com/datamade/dedupe) built by Forest Gregg and Derek Eder based on the work of Mikhail Bilenko. This algorithm asks you to give a number of examples of records from each dataset that are the same -- this information is extrapolated to link the rest of the dataset.

```bash
$ csvmatch data1.csv data2.csv --fuzzy
```

The more examples you give it, the better the results will be. At minimum, you should try to provide 10 positive matches and 10 negative matches.

### Fuzzy matching: Levenshtein

[Damerau-Levenshtein] (https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance) is a string distance metric, which counts the number of changes that would have to be made to transform one string into another.

For two strings to be considered a match, we require 60% of the longer string to be the same as the shorter one.

```bash
$ csvmatch data1.csv data2.csv --fuzzy levenshtein

name,name
George Smiley,George SMILEY
Toby Esterhase,Tony Esterhase
Peter Guillam,Peter Guillam
```

Here this matches Toby Esterhase and Tony Esterhase. Levenshtein is good at picking up typos and other small differences in spelling.

### Fuzzy matching: Metaphone

[Double Metaphone] (https://en.wikipedia.org/wiki/Metaphone#Double_Metaphone) is a phonetic matching algorithm, which compares strings based on how they are pronounced:

```bash
$ csvmatch data1.csv data2.csv --fuzzy metaphone

name,name
George Smiley,George SMILEY
Peter Guillam,Peter Guillam
Connie Sachs,Konny Saks
```

Here this matches Connie Sachs and Konny Saks, despite their very different spellings. Metaphone will pick up such differences.
