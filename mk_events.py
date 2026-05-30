#!/usr/bin/env python3
"""
This script emits LaTeX for the event listings to be copied into the survival guide.

Export the events data from the Google Sheet as a CSV and save it.  Then pass it as
the command line argument.
"""
import sys
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

from common import latexize, collect_non_ascii_chars, report_unicode_warnings

FORM_RENAME_MAP = {
    'What shall we call your Event?': 'title',
    'Who is hosting? Theme Camp or Your name': 'host',
    'Which day(s) will your event take place?': 'days',
    'What time will your event start?': 'start',
    'What time will your event end?': 'end',
    'Description of your play-learn-workshop-event for the Pocket Guide!': 'description',
    'Select a theme of your event for Pocket Guide!': 'theme',
    'If Materials Are Used, Will You Provide Them?': 'bring',
    'Not a Theme Camp? Please give us a location (art installation, lakeside, effigy, temple.. etc)': 'location',
}

FORM_COLUMNS = ['title', 'host', 'location', 'days', 'start', 'end', 'theme', 'description', 'bring']
UNICODE_FIELDS = ['title', 'host', 'location', 'description', 'bring']

SECTION_ORDER = ['Thursday', 'Friday', 'Saturday', 'Sunday']

MEANINGLESS_VALUES = {'nan', 'n/a', 'na', 'none', 'no', 'no materials used'}
EVENT_THEME_ICONS = {
    'Performance': r'{\color{purple} \faTheaterMasks}',
    'Event': r'{\color{purple} \faIcon[regular]{calendar-alt}}',
    'Party': r'{\color{purple} \faIcon{glass-martini-alt}}',
    'Workshop': r'{\color{purple} \faGraduationCap}',
    'Game': r'{\color{purple} \faChess}',
    'Music': r'{\color{purple} \faMusic}',
    'Food': r'{\color{purple} \faPizzaSlice}',
    'Non-alcoholic-Drinks': r'{\color{purple} \faCoffee}',
    'Tour': r'{\color{purple} \faIcon{bus-alt}}',
    'Fire': r'{\color{purple} \faIcon{fire-alt}}',
    'Chill': r'{\color{purple} \faUmbrellaBeach}',
    'Other': r'{\color{purple} \faIcon{question-circle}}',
}

UPSIDE_DOWN_EVENT_IDENTIFIERS = {
    'Upside down time w/ River',
    'ɹǝʌᴉɹ /ʍ ǝɯᴉʇ uʍop ǝpᴉsdn',
}


def format_event_title(title):
    raw_title = '' if pd.isnull(title) else str(title)
    if any(identifier in raw_title for identifier in UPSIDE_DOWN_EVENT_IDENTIFIERS):
        # Render this one title upside down in LaTeX without relying on fragile Unicode glyphs.
        return r'\rotatebox[origin=c]{180}{Upside down time w/ River}'
    return latexize(raw_title)


def make_event_theme(theme):
    return EVENT_THEME_ICONS.get(theme, '')


def compile_event_output(title, host, location, time, description, bring):
    output = (
        '\\vbox{\n'
        + title
        + '\\begin{description}[leftmargin=2em,noitemsep,style=nextline]\n'
        + host
        + location
        + time
        + bring
        + '\\end{description}\n'
        + description
        + '}\n\n'
    )
    return output.replace('\n', '\n\n')


def extract_dates(day_str):
    if pd.isnull(day_str):
        return []
    return re.findall(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2}', str(day_str))


def infer_event_year(df, input_path):
    path_match = re.search(r'(20\d{2})', input_path)
    if path_match:
        return int(path_match.group(1))

    if 'Timestamp' in df.columns:
        timestamp_values = df['Timestamp'].dropna().astype(str)
        for value in timestamp_values:
            timestamp_match = re.search(r'(20\d{2})', value)
            if timestamp_match:
                return int(timestamp_match.group(1))

    return datetime.now().year


def parse_date(day_str, year):
    return datetime.strptime(f"{day_str}, {year}", "%A, %B %d, %Y")


def has_meaningful_value(value):
    if pd.isnull(value):
        return False

    text = str(value).strip()
    if text == '':
        return False

    lowered = text.lower()
    return lowered not in MEANINGLESS_VALUES


def make_optional_field(icon, text):
    if not has_meaningful_value(text):
        return ''
    return rf'\item[{icon}] {latexize(text)}' + '\n'


def init_section_buffers():
    return {
        day: f'\\section[{day}]{{{day} Events}}\n\n'
        for day in SECTION_ORDER
    }


def collect_row_unicode_warnings(row):
    non_ascii = set()
    for field in UNICODE_FIELDS:
        non_ascii.update(collect_non_ascii_chars(getattr(row, field)))
    return sorted(non_ascii)


if __name__ == '__main__':
    input_path = sys.argv[1]
    df = pd.read_csv(input_path)
    event_year = int(sys.argv[2]) if len(sys.argv) > 2 else infer_event_year(df, input_path)
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path('events_raw.tex')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Rename from the original Google form names to something a little more reasonable.

    df.rename(columns=FORM_RENAME_MAP, inplace=True)
    df = df[FORM_COLUMNS]
    df = df.infer_objects()

    # For events that occur over more than one day, we must replicate that even for each of those extra days
    df['day_list'] = df['days'].apply(extract_dates)

    df_expanded = df.explode('day_list').drop(columns='days')
    df_expanded = df_expanded.rename(columns={'day_list': 'day_str'})
    df_expanded['date'] = df_expanded['day_str'].apply(lambda day_str: parse_date(day_str, event_year))
    df_expanded = df_expanded.drop(columns='day_str')

    df_expanded['start_time'] = pd.to_datetime(df_expanded['start'], format='%I:%M:%S %p').dt.time
    df_expanded['end_time'] = pd.to_datetime(df_expanded['end'], format='%I:%M:%S %p').dt.time

    df_expanded['day'] = df_expanded['date'].dt.day_name()

    df_expanded.sort_values(by=['date', 'start_time'], inplace=True)
    unicode_warnings = []
    ongoing = ''
    section_buffers = init_section_buffers()

    # Strip any leading or trailing whitespace from the camp name and theme
    # df_expanded = df_expanded.apply(lambda col: col.str.strip() if col.dtype == 'object' and col.str.strip().notna().any() else col)

    for _, row in df_expanded.iterrows():
        print(f'Processing {row.title}...')

        non_ascii = collect_row_unicode_warnings(row)
        if non_ascii:
            unicode_warnings.append((row.title, non_ascii))

        title = (
            r'\subsection*{\begin{tblr}{Q[0.8\columnwidth]X[halign=r, valign=t]}'
            + f'{format_event_title(row.title)} & {make_event_theme(row.theme)}'
            + r'\end{tblr}}' + '\n'
        )

        host = make_optional_field(r'{\color{violet} \faUserFriends}', row.host)
        location = make_optional_field(r'{\color{teal} \faMapMarked}', row.location)

        day = row.day # day of week

        time = (
            r'\item[{\color{cyan} \faClock[regular]}] '
            + f'{row.start_time}--{row.end_time}\n'
        )
        description = '{}'.format(latexize(row.description)) + '\n'

        bring = make_optional_field(r'{\color{red} \faSuitcase}', row.bring)

        output = compile_event_output(title, host, location, time, description, bring)

        if day == 'Everyday':
            ongoing += output
        elif day in section_buffers:
            section_buffers[day] += output

    with output_path.open('w') as f:
        ordered_sections = ''.join(section_buffers[day] for day in SECTION_ORDER)
        f.write(ongoing + ordered_sections)

    report_unicode_warnings(unicode_warnings, stream=sys.stderr)
