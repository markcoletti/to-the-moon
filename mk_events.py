#!/usr/bin/env python3
"""
This script emits LaTeX for the event listings to be copied into the survival guide.

Export the events data from the Google Sheet as a CSV and save it.  Then pass it as
the command line argument.
"""
import sys

import pandas as pd

from common import latexize

ongoing = '' # title for ongoing saved separately
thursday = '\section[Thursday]{Thursday Events}\n\n'
friday = '\section[Friday]{Friday Events}\n\n'
saturday = '\section[Saturday]{Saturday Events}\n\n'
sunday = '\section[Sunday]{Sunday Events}\n\n'

def makeEventTheme(theme):
  if theme == 'Performance':
    return '{\color{purple} \\faTheaterMasks}'
  elif theme == 'Event':
    return '{\color{purple} \\faIcon[regular]{calendar-alt}}'
  elif theme == 'Party':
    return '{\color{purple} \\faIcon{glass-martini-alt}}'
  elif theme == 'Workshop':
    return '{\color{purple} \\faGraduationCap}'
  elif theme == 'Game':
    return '{\color{purple} \\faChess}'
  elif theme == 'Music':
    return '{\color{purple} \\faMusic}'
  elif theme == 'Food':
    return '{\color{purple} \\faPizzaSlice}'
  elif theme == 'Non-alcoholic-Drinks':
    return '{\color{purple} \\faCoffee}'
  elif theme == 'Tour':
    return '{\color{purple} \\faIcon{bus-alt}}'
  elif theme == 'Fire':
    return '{\color{purple} \\faIcon{fire-alt}}'
  elif theme == 'Chill':
    return '{\color{purple} \\faUmbrellaBeach}'
  else:
    return ''


def compileEventOutput(title, host, location, time, description, bring):
  output = '\\vbox{\n' + title + "\\begin{description}[leftmargin=2em,noitemsep,style=nextline]\n" + host + location + time +\
            bring + "\end{description}\n" + description.replace('&', '\\&') + '}\n\n'
  # output = output.replace('&', '\\&')
  output = output.replace('\n', '\n\n')
  return output





if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1])

    # For 2024 I manually cleaned up the events and saved it to 'final_events.csv',
    # and then ran the following code to generate the LaTeX

    #
    #
    # df.rename(columns={'What shall we call your Event?': 'title',
    #                    'Who is hosting? Theme Camp or Your name': 'host',
    #                    'Which day would you prefer? ': 'day',
    #                    'What time slot would you prefer? ': 'time_pretty',
    #                    'Description of your play-learn-workshop-event for the Pocket Guide!': 'description',
    #                    'Select a theme of your event for Pocket Guide!': 'theme',
    #                    'If Materials Are Used, Will You Provide Them?': 'bring',
    #                    'Not a Theme Camp? Please give us a location (art installation, lakeside, effigy, temple.. etc)': 'location'},
    #           inplace=True)
    # df = df[['title', 'host', 'location', 'day', 'time_pretty', 'time_tech', 'theme', 'description', 'bring']]
    # df = df.infer_objects()
    df.startTime = pd.to_datetime(df['startTime'], format='mixed')
    df.sort_values(by='startTime', inplace=True)
    #
    # # Strip any leading or trailing whitespace from the camp name and theme
    # df = df.map(lambda x: x.strip() if isinstance(x, str) else x)


    for index, row in df.iterrows():
        title = '\subsection*{\\begin{tblr}{Q[0.8\columnwidth]X[halign=r, valign=t]}' + '{} & {}'.format(
            row.title.replace('&', '\\&'), makeEventTheme(row.theme) + '\end{tblr}}\n')
        print(f'Processing {row.title}...')
        if not pd.isnull(row.host) and row.host != '':
            host = '\item[{\color{violet} \\faUserFriends}] ' + '{}'.format(row.host) + '\n'
        else:
            host = ''
        locationField = row.location
        location = ''
        if locationField != '':
            location = '\item[{\color{teal} \\faMapMarked}] ' + '{}'.format(locationField) + '\n'
        theme = makeEventTheme(row.theme)
        day = row.shortDay.split(',')[0] # Get the three letter day of the week
        time = '\item[{\color{cyan} \\faClock[regular]}] ' + '{}'.format(row.shortTime) + '\n'
        description = '{}'.format(latexize(row.description)) + '\n'
        if not pd.isnull(row.bring) or row.bring != '':
            bring = '\item[{\color{red} \\faSuitcase}] ' + '{}'.format(row.bring) + '\n'
        else:
            bring = ''
        output = compileEventOutput(title, host, location, time, description, bring)
        if day == 'Everyday':
            ongoing += output
        elif day == 'Thu':
            thursday += output
        elif day == 'Fri':
            friday += output
        elif day == 'Sat':
            saturday += output
        elif day == 'Sun':
            sunday += output

    with open('events_raw.tex', 'w') as f:
        f.write(ongoing + thursday + friday + saturday + sunday)