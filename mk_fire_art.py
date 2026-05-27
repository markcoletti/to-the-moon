#!/usr/bin/env python3
"""
    Script for emitting the LaTeX for the fire art section in the art chapter.  It will create art_fire_raw.tex that should be
    uploaded to the `flight-only` folder in the TTM Survival Guide Overleaf project.

    Usage: mk_fire_art.py <fire art CSV file from google forms>
"""
import sys
import pandas as pd

from datetime import datetime

from simple.events import latexize


if __name__ == '__main__':
    art_df = pd.read_csv(sys.argv[1])

    # Let's get some sensible column names
    art_df.rename(columns={'Legal Name' : 'name',
                           'Do you have a burner name or other name you prefer to go by?' : 'burner_name',
                           'What are your pronouns? (Ex. She/Her, They/Them, etc.)' : 'pronouns',
                           'Brief description of your fire Art' : 'description',
                           }, inplace=True)

    # Now let's sort by name
    art_df.sort_values(by=['name'], inplace=True)

    with open('art_fire_raw.tex', 'w') as art_fire_raw:
        # TODO we need to do this for the other _raw.tex files so that we can check the uploaded versions
        # by the timestamp at the top of the file to ensure we have the most recent version.
        header = f'% art_fire_raw.tex generated at {str(datetime.now())}\n%\n%\n\n\n'
        art_fire_raw.writelines([header])

        for row in art_df.itertuples():
            art_fire_raw.write('\\vbox{\n') # to ensure that the art description doesn't get split across pages

            if row.burner_name is not None and not pd.isnull(row.burner_name):
                artist = row.burner_name
            else:
                artist = row.name


            # Only add pronouns if they've been specified
            if row.pronouns is not None and not pd.isnull(row.pronouns):
                artist += ' (' + row.pronouns + ')'

            art_fire_raw.write(f'\section*{{{artist}}}\n\n')
            # art_fire_raw.write(f'By {artist}')

            art_fire_raw.write('\n\n')

            art_fire_raw.write(latexize(row.description))

            art_fire_raw.write('\n}\n')

            art_fire_raw.write('\n\n')
