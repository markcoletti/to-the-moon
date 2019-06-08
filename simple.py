#!/usr/bin/env python3
"""
    Take a *simple* CSV of name, description and blat out \section*{name} description

    The art and theme camps follow this model.  Great! \o/

    Fields that I use:
    Name, Description

    And I just need to emit

    \subsection*{name}

    Description
"""
import csv
import sys

if __name__ == '__main__':
    with open(sys.argv[1]) as csv_file:
        csv_reader = csv.reader(csv_file)

        # Skip the header
        next(csv_reader)

        for i, item in enumerate(csv_reader):
            print('\section*{', item[0], '}', sep='')
            print(item[1], '\n\n')


