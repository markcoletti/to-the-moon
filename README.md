# to-the-moon
To the Moon Survival Guide related code.

This code written by Mark "Piprrr" Coletti and Andy "Raptor" Berres.

Most of this code takes the output of Google forms, which is a spreadsheet, and outputs LaTeX code that can be
copied into the Survival Guide.

The directory `simple` contains older scripts that generates simple LaTeX for arts, events, and camps.  Basically,
just creates `\sections` and `\subsections` for each entry.  More recent versions in this directory level use 
additonal information to share additional information, such as event categories and theme camp attributes.


* `mk_camps.py` - Generates LaTeX code for theme camps.
