#!/usr/bin/env python3
"""
This script emits LaTeX for the event listings to be copied into the survival guide.

Export the events data from the Google Sheet as a CSV and save it.  Then pass it as
the command line argument.
"""
import sys
import re
from datetime import datetime
import pandas as pd

from common import latexize

# We append the events to each of these strings as we go along, then write
# them all out at once at the very end to the output .tex file.
ongoing = '' # title for ongoing saved separately
thursday = '\section[Thursday]{Thursday Events}\n\n'
friday = '\section[Friday]{Friday Events}\n\n'
saturday = '\section[Saturday]{Saturday Events}\n\n'
sunday = '\section[Sunday]{Sunday Events}\n\n'

def make_event_theme(theme):
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
  elif theme == 'Other':
      return '{\color{purple} \\faIcon{question-circle-o}'
  else:
    return ''


def compile_event_output(title, host, location, time, description, bring):
  output = '\\vbox{\n' + title + "\\begin{description}[leftmargin=2em,noitemsep,style=nextline]\n" + host + location + time + \
            bring + "\end{description}\n" + description.replace('&', '\\&') + '}\n\n'
  # output = output.replace('&', '\\&')
  output = output.replace('\n', '\n\n')
  return output


def extract_dates(day_str):
    return re.findall(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2}', day_str)


def parse_date(day_str):
    return datetime.strptime(f"{day_str}, 2025", "%A, %B %d, %Y")


if __name__ == '__main__':
    df = pd.read_csv(sys.argv[1])

    # Rename from the original Google form names to something a little more reasonable.

    df.rename(columns={'What shall we call your Event?': 'title',
                       'Who is hosting? Theme Camp or Your name': 'host',
                       'Which day(s) will your event take place?': 'days',
                       'What time will your event start?' : 'start',
                       'What time will your event end?' : 'end',
                       'Description of your play-learn-workshop-event for the Pocket Guide!': 'description',
                       'Select a theme of your event for Pocket Guide!': 'theme',
                       'If Materials Are Used, Will You Provide Them?': 'bring',
                       'Not a Theme Camp? Please give us a location (art installation, lakeside, effigy, temple.. etc)': 'location'},
              inplace=True)
    df = df[['title', 'host', 'location', 'days', 'start', 'end', 'theme', 'description', 'bring']]
    df = df.infer_objects()

    # For events that occur over more than one day, we must replicate that even for each of those extra days
    df['day_list'] = df['days'].apply(extract_dates)

    df_expanded = df.explode('day_list').drop(columns='days')
    df_expanded = df_expanded.rename(columns={'day_list': 'day_str'})
    df_expanded['date'] = df_expanded['day_str'].apply(parse_date)
    df_expanded = df_expanded.drop(columns='day_str')

    df_expanded['start_time'] = pd.to_datetime(df_expanded['start'], format='%I:%M:%S %p').dt.time
    df_expanded['end_time'] = pd.to_datetime(df_expanded['end'], format='%I:%M:%S %p').dt.time

    df_expanded['day'] = df_expanded['date'].dt.day_name()

    df_expanded.sort_values(by=['date', 'start_time'], inplace=True)

    # Strip any leading or trailing whitespace from the camp name and theme
    # df_expanded = df_expanded.apply(lambda col: col.str.strip() if col.dtype == 'object' and col.str.strip().notna().any() else col)

    for index, row in df_expanded.iterrows():
        print(f'Processing {row.title}...')

        title = '\subsection*{\\begin{tblr}{Q[0.8\columnwidth]X[halign=r, valign=t]}' + '{} & {}'.format(
            row.title.replace('&', '\\&'), make_event_theme(row.theme) + '\end{tblr}}\n')

        if not pd.isnull(row.host) and row.host != '':
            host = '\item[{\color{violet} \\faUserFriends}] ' + '{}'.format(row.host) + '\n'
        else:
            host = ''

        locationField = row.location
        location = ''
        if locationField != '':
            location = '\item[{\color{teal} \\faMapMarked}] ' + '{}'.format(locationField) + '\n'

        theme = make_event_theme(row.theme)

        day = row.day # day of week

        time = ('\item[{\color{cyan} \\faClock[regular]}] ' + '{}'.format(row.start_time) + '--' +
                '{}'.format(row.end_time) + '\n')
        description = '{}'.format(latexize(row.description)) + '\n'

        if not pd.isnull(row.bring) or row.bring != '':
            bring = '\item[{\color{red} \\faSuitcase}] ' + '{}'.format(row.bring) + '\n'
        else:
            bring = ''

        output = compile_event_output(title, host, location, time, description, bring)

        if day == 'Everyday':
            ongoing += output
        elif day == 'Thursday':
            thursday += output
        elif day == 'Friday':
            friday += output
        elif day == 'Saturday':
            saturday += output
        elif day == 'Sunday':
            sunday += output

    with open('events_raw.tex', 'w') as f:
        f.write(ongoing + thursday + friday + saturday + sunday)