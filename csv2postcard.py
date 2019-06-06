#!/usr/bin/env python3
"""
    Used to create LaTeX output for a postcard from a CSV file.  This creates
    two pages for a 3.5" x 5" postcard for each violation.


usage: csv2postcard.py [-h] [--in-file IN_FILE] [--out-file OUT_FILE]
                         [--threshold THRESHOLD]

Generate a postcard LaTeX file

optional arguments:
  -h, --help            show this help message and exit
  --in-file IN_FILE, -i IN_FILE
                        CSV file of curbside violations
  --out-file OUT_FILE, -o OUT_FILE
                        Where to write the LaTeX
  --threshold THRESHOLD, -t THRESHOLD
                        Threshold for number of violations to merit a postcard
"""
import sys
import argparse
import csv
from pathlib import Path

import cardlatex


# This is the script return code if we cannot open the curbside violations CSV file
NO_CSV_FILE_ERROR = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a postcard LaTeX file')

    parser.add_argument('--in-file','-i', help='CSV file of curbside violations')
    parser.add_argument('--out-file', '-o', help='Where to write the LaTeX')
    parser.add_argument('--threshold', '-t', type=int, default=3, help='Threshold for number of violations to merit a postcard')

    args = parser.parse_args()

    curbside_violation_path = Path(args.in_file)

    if not curbside_violation_path.exists():
        print(violations_csv_file, 'does not exist ... exiting')
        sys.exit(NO_CSV_FILE_ERROR)

    # We've got curbside violations, so let's build a dictionary of violations keyed by address
    aggregated_violations = {}

    with curbside_violation_path.open('r') as curbside_violation:
        violations_reader = csv.DictReader(curbside_violation)

        for violation in violations_reader:
            # Fetch the record for this address and create an empty list if this is the first time we're referencing it
            house_address = violation['HOUSE #'] + violation['STREET']
            single_address = aggregated_violations.setdefault(house_address, [])

            # Accumulation this violation
            single_address.append(violation)

    # Now let's cook those down to violators that exceed the given threshold
    viable_violations = {key:value for key, value in aggregated_violations.items() if len(value) > args.threshold}

    print('Considering ', len(viable_violations), 'violations out of', len(aggregated_violations), 'violations using a threshold of', args.threshold)

    # Now blat out the LaTeX for waste management violation postcards
    with Path(args.out_file).open('w') as latex_postcards_file:
        cardlatex.write_latex_preamble(latex_postcards_file)

        for viable_violation in viable_violations.values():
            cardlatex.process_violation(viable_violation, latex_postcards_file)

        cardlatex.write_latex_end(latex_postcards_file)
