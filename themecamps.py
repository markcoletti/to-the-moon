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

if __name__ == '__main__':
    with open('data/themecamps.csv') as themecamps:
        themecamps_reader = csv.reader(themecamps)

        for i, theme_camp in enumerate(themecamps_reader):
            print(i, ':', theme_camp[0], theme_camp[1])

