#!/usr/bin/env python3
"""
Script for emitting the LaTeX for the art cars setion of the art chapter.  It will create art_mutant_vehicles.tex
that should be uploaded to the `flight-only` folder in the TTM Survival Guide Overleaf project.

    Usage: mk_art_cars.py <art CSV file from google forms>
"""
import sys
import pandas as pd

from datetime import datetime

from simple.events import latexize


if __name__ == '__main__':
    art_df = pd.read_csv(sys.argv[1])

    # Let's get some sensible column names
    art_df.rename(columns={'MV Name' : 'name',
                           'MV Description' : 'description',
                           'MV Owner' : 'artist'
                           }, inplace=True)

    # Now let's sort by name
    art_df.sort_values(by=['name'], inplace=True)

    with open('art_mutant_vehicles.tex', 'w') as art_mutant_vehicles:
        # TODO we need to do this for the other _raw.tex files so that we can check the uploaded versions
        # by the timestamp at the top of the file to ensure we have the most recent version.
        header = f'% art_mutant_vehicles.tex generated at {str(datetime.now())}\n%\n%\n\n\n'
        art_mutant_vehicles.writelines([header])

        for row in art_df.itertuples():
            art_mutant_vehicles.write('\\vbox{\n') # to ensure that the art description doesn't get split across pages
            art_mutant_vehicles.write(f'\section*{{{row.name}}}\n\n')

            artist = row.artist
            # Only add pronouns if they've been specified
            # if row.pronouns is not None and not pd.isnull(row.pronouns):
            #     artist += ' (' + row.pronouns + ')'
            art_mutant_vehicles.write(f'By {artist}')

            art_mutant_vehicles.write('\n\n')

            art_mutant_vehicles.write(latexize(row.description))

            art_mutant_vehicles.write('\n}\n')

            art_mutant_vehicles.write('\n\n')
