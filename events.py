#!/usr/bin/env python3
"""
    Wrangle the events CSV into LaTeX


"""
import csv
import sys
import pandas as pd





if __name__ == '__main__':

    with open(sys.argv[0]) as csv_file:
        events_df = pd.read_csv(csv_file)

        # pull out the ongoing events first and blat those out

        # Then sort by date, start time and end time
        
        # Then process each record.


