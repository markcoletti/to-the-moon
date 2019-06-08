#!/usr/bin/env python3
"""
    Wrangle the events CSV into LaTeX


"""
import csv
import sys
import pandas as pd


def latexize(text):
    """ Escape all LaTeX hostile characters

    :param text: contains text that may contain LaTeX unfriendly characters.
    :return: text with strings properly escaped
    """
    return text.replace('&','\\&').replace('#','\\#').replace('{','\\{').replace('}','\\}').replace('_','\\_')

def process_daily(daily_events):
    """ Blat out the LaTeX for the daily events

    :param daily_events: dataframe of just the daily events
    :return: None
    """
    def print_event(event):
        print('\\vbox{')
        print('\subsection*{',event.Title,'}',sep='')
        print('\\begin{description}[leftmargin=6em,noitemsep,style=nextline]')
        print('   \item[Location:]', event.Location)
        if not pd.isnull(event.Host):
            print('    \item[Host:]', event.Host)
        if event['Start Time'] != 'Ongoing event':
            print('    \item[Start time:]', event['Start Time'])
        print('\end{description}\n')
        print(latexize(event.Description),'\n')
        if not pd.isnull(event.Notes):
            print(latexize(event.Notes))

        print('}\n')

    print('\section*{Ongoing}\n')

    for index, event in daily_events.iterrows():
        print_event(event)


if __name__ == '__main__':

    # with open(sys.argv[0]) as csv_file:
    events_df = pd.read_csv(sys.argv[1])

    # pull out the ongoing events first and blat those out
    process_daily(events_df[events_df.Date == 'Daily'])

    # Then sort by date, start time and end time

    # Then process each record.


