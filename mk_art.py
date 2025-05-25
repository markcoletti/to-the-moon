#!/usr/bin/env python3
"""
    Script for emitting the LaTeX for the art chapter.  It will create art_raw.tex that should be
    uploaded to the `flight-only` folder in the TTM Survival Guide Overleaf project.

    Usage: mk_art.py <art CSV file from google forms>
"""
import sys
import pandas as pd


if __name__ == '__main__':
    art_df = pd.read_csv(sys.argv[1])

    art_df.rename(columns={'What is the Name of your Art Project?' : 'name',
                           'Public Description of your Art Project' : 'description',
                           'Artist Name ' : 'artist',
                           'Artist Pronouns (Ex. She/They, He/Him, etc)' : 'pronouns',
                           })