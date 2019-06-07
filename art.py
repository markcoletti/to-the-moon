#!/usr/bin/env python3
"""
    Take a CSV of art info and convert them into LaTeX for embedding in the Flight Manual

    Fields that I use:
    Name Of Installation, Describe The Installation

    And I just need to emit

    \subsection*{name}

    Description
"""
import csv

if __name__ == '__main__':
    with open('data/sorted_art.csv') as art_file:
        art_reader = csv.reader(art_file)

        # Skip the header
        next(art_reader)

        for i, art in enumerate(art_reader):
            print('\section*{', art[3], '}',sep='')
            print(art[4], '\n\n')


