#!/usr/bin/env python3
"""
This script emits LaTeX for the camp listings to be copied into the survival guide.

Export the camp data from the Google Sheet as a CSV and save it.  Then pass it as
the command line argument.
"""
import sys
from pathlib import Path

import pandas as pd

from common import latexize

def makeCampTheme(theme):
    if pd.isnull(theme):
        return ''

    icons = ''
    if 'Adult' in theme:
        icons += '\\faUserAstronaut '
    if 'Kids' in theme:
        icons += '\\faChild '
    if 'Art' in theme:
        icons += '\\faPalette '
    if 'Bar' in theme:
        icons += '\\faIcon{glass-martini-alt} '
    if 'Drinks-non-alcoholic' in theme:
        icons += '\\faCoffee '
    if 'Food' in theme:
        icons += '\\faPizzaSlice '
    if 'Chill' in theme:
        icons += '\\faUmbrellaBeach '
    if 'Games' in theme:
        icons += '\\faDice '
    if 'Learning' in theme:
        icons += '\\faGraduationCap '
    if 'Music-silent' in theme:
        icons += '\\faHeadphones '
    elif 'Music' in theme:
        icons += '\\faMusic '
    if 'Performance' in theme:
        icons += '\\faTheaterMasks '
    return icons
    # \\faChild \\faBaby \\faBasketballBall \\faCameraRetro \\faCampground \\faCoffee \\faCouch \\faDice \\faHiking \\faLeaf \\faUmbrellaBeach \\faWalking
    # \\faIcon[regular]{lightbulb} \\faMoon \\faMortarPestle \\faMugHot \\faPeace \\faRainbow \\faRunning \\faSeedling  \\faStar \\faSun \faUserAstronaut \\faUser


def compileCampOutput(camp, theme, description, location='', notes=''):
    description = latexize(description) # escape any LaTeX hostile characters
    if camp in ["We're Occult", 'World Spirits']:
        output = '\\vbox{\n' + '\\subsection*{\\begin{tblr}{Q[0.6\\columnwidth]X[halign=r, valign=t]}' + '{}'.format(
            camp.replace('&', '\\&')) + '& {\\color{purple} ' + \
                 theme + '}\\end{tblr}\\vspace{-1em}}\n' + location + description.replace('&', '\\&').replace('#',
                                                                                                             '\\#') + notes + '\n}\n\n'
    else:
        output = '\\vbox{\n' + '\\subsection*{\\begin{tblr}{Q[0.7\\columnwidth]X[halign=r, valign=t]}' + '{}'.format(
            camp.replace('&', '\\&')) + '& {\\color{purple} ' + \
                 theme + '}\\end{tblr}\\vspace{-1em}}\n' + location + description.replace('&', '\\&').replace('#',
                                                                                                             '\\#') + notes + '\n}\n\n'
    output = output.replace('\n', '\n\n')
    return output



if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('camps_raw.tex')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.rename(columns={'Theme Camp Name': 'camp',
                       'In what "genres" would you classify your camp? Check all that apply.': 'theme',
                       #  'Notes': 'notes',
                       'Public Camp Description': 'description'}, inplace=True)
    df = df[['camp', 'theme',
             'description']]  # update to reflect inputs -- note that we could add neighborhoods here if we have those
    df.sort_values(by='camp', inplace=True)

    output = ''

    # Strip any leading or trailing whitespace from the camp name and theme
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    with output_path.open('w') as f:

        for index, row in df.iterrows():
            camp = row.camp
            theme = makeCampTheme(row.theme)
            description = '{}'.format(row.description) + '\n'
            # location = '{\color{teal} \\faMapMarked}~~' + row[3].strip() + '\n'
            # notes =  '{}'.format(row[4].strip())
            # if row[4].strip() == 'skip':
            #   continue
            # elif notes != '':
            #   notes = '\n\\faInfoCircle~~' + notes
            print(f'Processing {camp}')
            output = compileCampOutput(camp, theme, description)

            f.write(output)

