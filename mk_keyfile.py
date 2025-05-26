#!/usr/bin/env python3
""" Used to generate LaTeX for art or camp map keys.

Usage: mk_keyfile.py <CSV file>

Output would be to stdout.  You should redirect output to desired target file.
"""
import pandas as pd
import argparse






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate LaTeX for art or camp map keys from a CSV file.")
    parser.add_argument('--key', type=str, default='order',
                        help='Name of field holding the map keys')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing "Name" and "id" columns.')
    args = parser.parse_args()

    map_keys_df = pd.read_csv(args.csv_file, usecols=["Name", args.key])

    # First do things in numeric order

    map_keys_df.sort_values(by=args.key, inplace=True, ignore_index=True)

    print("\\subsection*{Numeric}")

    print("\begin{multicols}{2}\n\\small\n")

    print("\\begin{itemize}[itemsep=.0125mm,parsep=2pt]")

    for _, row in map_keys_df.iterrows():
        name = row["Name"].replace("&", "\\&")
        print(f"\t\\item[\\textbf{{ {row['id']} }}] {name}")

    print("\\end{itemize}")
    print("\n\\end{multicols}\n")

    # Now do things in alphabetical order

    print("\subsection*{Alphabetic}")
    map_keys_df.sort_values(by="Name", inplace=True, ignore_index=True)

    print("\begin{multicols}{2}\n\\small\n")

    print("\\begin{itemize}[itemsep=.0125mm,parsep=2pt]")


    print("\\begin{itemize}[itemsep=.0125mm,parsep=2pt]")

    for _, row in map_keys_df.iterrows():
        name = row["Name"].replace("&", "\\&")
        print(f"\t\\item[\\textbf{{ {row['id']} }}] {name}")

    print("\\end{itemize}")


    print("\\end{itemize}")
    print("\n\\end{multicols}\n")

