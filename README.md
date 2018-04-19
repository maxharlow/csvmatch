CSV Match
=========

Find (fuzzy) matches between two CSV files in the terminal.

Tested on Python 3.6 and 2.7.

[There's a tutorial on how CSV Match can be used for investigative journalism here.](https://github.com/maxharlow/tutorials/tree/master/find-connections-with-fuzzy-matching)


Installing
----------

    pip install csvmatch


Usage
-----

Say you have one CSV file such as:

    name,location,codename
    George Smiley,London,Beggerman
    Percy Alleline,London,Tinker
    Roy Bland,London,Soldier
    Toby Esterhase,Vienna,Poorman
    Peter Guillam,Brixton,none
    Bill Haydon,London,Tailor
    Oliver Lacon,London,none
    Jim Prideaux,Slovakia,none
    Connie Sachs,Oxford,none

And another such as:

    Person Name,Location
    Maria Andreyevna Ostrakova,Russia
    Otto Leipzig,Estonia
    George SMILEY,London
    Peter Guillam,Brixton
    Konny Saks,Oxford
    Saul Enderby,London
    Sam Collins,Vietnam
    Tony Esterhase,Vienna
    Claus Kretzschmar,Hamburg

You can then find which names are in both files:

    $ csvmatch data1.csv data2.csv \
        --fields1 name \
        --fields2 'Person Name'

You can also compare multiple columns, so if we wanted to find which name and location combinations are in both files we could:

    $ csvmatch data1.csv data2.csv \
        --fields1 name location \
        --fields2 'Person Name' Location

By default, all columns are used to compare rows. Specific columns can be also be given to be compared -- these should be in the same order for both files. Column headers with a space should be enclosed in quotes. Matches are case-sensitive by default, but can be made case-insensitive with `-i`.

There are also options to ignore non-alphanumeric characters (`-a`), to convert to the latin alphabet (`-n`), and to sort words (`-s`) before comparisons. Specific terms can also be filtered out before comparisons by passing a text file and the `-l` argument. A predefined list of common English name prefixes (Mr, Ms, etc) can be used with `-t`.

By default the columns used in the output are the same ones used for matching. Other sets of columns can be specified using the `--output` parameter. This takes a space-separated list of column names, each prefixed with a number and a dot indicating which file that field is from:

    $ csvmatch data1.csv data2.csv \
        --fields1 name location \
        --fields2 'Person Name' Location \
        --output 1.name '2.Person Name' 2.Location \
        > results.csv

There are also some special column definitions. `1*` and `2*` expand into all columns from that file. Where a fuzzy matching algorithm has been used `degree` will add a column with a number between 0 - 1 indicating the strength of each match.

By default the two files are linked using an inner join -- only successful matches are returned. However using `-f` you can specify a `left-outer` join which will return everything from the first file, whether there was a match or not. You can also specify `right-outer` to do the same but for the second file, and `full-outer` to return everything from both files.

We can combine some of the above options to perform operations alike Excel's `VLOOKUP`. So if we wanted to add a column to `data2.csv` giving the codename of each person that is specified in `data1.csv`:

    $ csvmatch data1.csv data2.csv \
        --fields1 name \
        --fields2 'Person Name' \
        --join right-outer \
        --output 2* 1.codename \
        > results.csv

### Fuzzy matching

CSV Match also supports fuzzy matching. This can be combined with any of the above options.

#### Bilenko

The default fuzzy mode makes use of the [Dedupe library](https://github.com/dedupeio/dedupe) built by Forest Gregg and Derek Eder based on the work of Mikhail Bilenko. This algorithm asks you to give a number of examples of records from each dataset that are the same -- this information is extrapolated to link the rest of the dataset.

    $ csvmatch data1.csv data2.csv --fuzzy

The more examples you give it, the better the results will be. At minimum, you should try to provide 10 positive matches and 10 negative matches.

#### Levenshtein

[Damerau-Levenshtein](https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance) is a string distance metric which counts the number of changes that would have to be made to transform one string into another.

For two strings to be considered a match, we require 60% of the longer string to be the same as the shorter one. This threshold can be modified by passing a number between 0.0 and 1.0 with `-t`.

    $ csvmatch data1.csv data2.csv --fuzzy levenshtein

    name,Person Name
    George Smiley,George SMILEY
    Toby Esterhase,Tony Esterhase
    Peter Guillam,Peter Guillam

Here this matches Toby Esterhase and Tony Esterhase -- Levenshtein is good at picking up typos and other small differences in spelling.

### Jaro

[Jaro-Winkler](https://en.wikipedia.org/wiki/Jaro–Winkler_distance) is a string distance metric which counts the number of transpositions that would be required to transform one string into another. It tends to work better than Levenshtein for shorter strings of text.

    $ csvmatch data1.csv data2.csv --fuzzy jaro

    name,Person Name
    George Smiley,George SMILEY
    Percy Alléline,Peter Guillam
    Percy Alléline,Sam Collins
    Toby Esterhase,Tony Esterhase
    Peter Guíllam,Peter Guillam
    Connie Sachs,Konny Saks

Here we can see a couple of incorrect matches for Percy Alléline, but Connie Sachs has matched.

#### Metaphone

[Double Metaphone](https://en.wikipedia.org/wiki/Metaphone#Double_Metaphone) is a phonetic matching algorithm, which compares strings based on how they are pronounced:

    $ csvmatch data1.csv data2.csv --fuzzy metaphone

    name,Person Name
    George Smiley,George SMILEY
    Peter Guillam,Peter Guillam
    Connie Sachs,Konny Saks

This shows a match for Connie Sachs and Konny Saks, despite their very different spellings.


A note on uniqueness
--------------------

Both with exact matches and fuzzy matching a name being the same is [no guarantee](https://en.wikipedia.org/wiki/List_of_most_popular_given_names) it refers to the same person. But the inverse is also true -- even with CSV Match, a combination of first inital and last name is likely to be sufficiently different from forename, middle names, and surname together that a match is unlikely. Moreso if one name includes a typo, either accidential or deliberate.
