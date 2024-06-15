#!/usr/bin/env python3
"""
    Take a CSV of theme camp descriptions and convert them into LaTeX for embedding in the Flight Manual

    Fields are very basic:
    Name, Description

    And I just need to emit

    \subsection*{name}

    Description
"""
import csv
import sys

if __name__ == '__main__':
    with open(sys.argv[1]) as themecamps:
        themecamps_reader = csv.reader(themecamps)

        next(themecamps_reader)

        for i, theme_camp in enumerate(themecamps_reader):
            print('	\item[\\textbf{' f'{theme_camp[1]}' '}] ' f'{theme_camp[2]}')

