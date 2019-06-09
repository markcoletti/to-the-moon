#!/usr/bin/env python3
"""
    Wrangle the events CSV into LaTeX


"""
import sys
import pandas as pd
import numpy as np
import time


def latexize(text):
    """ Escape all LaTeX hostile characters

    :param text: contains text that may contain LaTeX unfriendly characters.
    :return: text with strings properly escaped
    """
    return text.replace('&','\\&').replace('#','\\#').replace('{','\\{').replace('}','\\}').replace('_','\\_')



def process_ongoing(ongoing_events):
    """ Blat out the LaTeX for the ongoing events

    :param ongoing_events: dataframe of just the ongoing events
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

    for index, event in ongoing_events.iterrows():
        print_event(event)


def process_daily(daily_events):
    """ Blat out the LaTeX for the daily events

    :param daily_events: *sorted* dataframe by date and starting time
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
        if not pd.isnull(event['End Time']):
            print('    \item[End time:]', event['End Time'])
        print('\end{description}\n')
        print(latexize(event.Description),'\n')
        if not pd.isnull(event.Notes):
            print(latexize(event.Notes))

        print('}\n')

    # We use this to track when we switch over to a new day.  If the last date is not the same as the current, then
    # we know we are starting a new day.
    last_date = daily_events.Date[0]

    print('\section*{',last_date,'}\n',sep='')

    for index, event in daily_events.iterrows():
        # print(index, event.Date, event['Start Time'], event['End Time'])

        if event.Date != last_date:
            # We've rolled over to a new day
            last_date = event.Date
            print('\section*{', last_date, '}\n', sep='')

        print_event(event)




if __name__ == '__main__':

    # with open(sys.argv[0]) as csv_file:
    events_df = pd.read_csv(sys.argv[1])

    # pull out the ongoing events first and blat those out
    # process_ongoing(events_df[events_df.Date == 'Daily'])

    # now pull out the
    daily_events = events_df[events_df.Date != 'Daily']

    # ALL OF THIS IS UNNECESSARY IF YOU SORT THE SPREADSHEET BY DATE AND START TIME FIRST.  ARGH.
    # # we have to *all kinds* of gymnastics to get the time data to where we can sort it.
    # daily_events = daily_events.replace('TBD', np.NaN) # TBD? We'll treat that starting time as a NaN, thank you
    #
    # # now convert the HH:MM AM/PM to an actual time object that we can sort on
    # daily_events['Start Time'] = daily_events['Start Time'].map(
    #     lambda x: time.strptime(x, '%H:%M %p') if not pd.isna(x) else np.NaN)
    #
    # # Define our ordinal values for days
    # days = ['Thursday', 'Friday', 'Saturday', 'Sunday']
    #
    # # ... and then remap all the dates to that ordinal type so we can sort on _that_, too
    # daily_events.Date = daily_events.Date.astype('category', ordered=True, categories=days)
    #
    # # Then FINALLY sort by date, start time
    # daily_events = daily_events.sort_values(['Date','Start Time'])
    #
    # Now, at long last, blat out the LaTeX for each of those
    process_daily(daily_events)



