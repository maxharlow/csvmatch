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
George Smiley
Peter Guillam
Connie Sachs
Saul Enderby
Sam Collins
Toby Esterhase
Claus Kretzschmar
```

You can then find the matches:

```bash
$ csvmatch data1.csv data2.csv

name,name
Peter Guillam,Peter Guillam
George Smiley,George Smiley
Toby Esterhase,Toby Esterhase
Connie Sachs,Connie Sachs
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

CSV Match also supports fuzzy matching. By default this makes use of the [Dedupe library] (https://github.com/datamade/dedupe) built by Forest Gregg and Derek Eder based on the work of Mikhail Bilenko. This algorithm asks you to give a number of examples of records from each dataset that are the same -- this information is extrapolated to link the rest of the dataset.

```bash
$ csvmatch dataX.csv dataY.csv --fuzzy
```

The more examples you give it, the better the results will be. At minimum, you should try to provide 10 positive matches and 10 negative matches.
