CSV Match
=========

Find matches between two CSV files in the terminal.

Requires either version 2 or 3 of Python, including `pip`.


Installing
----------

Install with Pip: `pip install csvmatch`.


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

You can also pipe either file in using `-` as a placeholder, eg. `cat data1.csv | csvmatch - data2.csv`
