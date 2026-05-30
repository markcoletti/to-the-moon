#!/usr/bin/env python3
"""Common helpers shared across generator scripts."""

import sys
import unicodedata


UNICODE_REPLACEMENTS = {
    # Common punctuation/symbol normalization.
    '—': '---',
    '–': '--',
    '…': r'\ldots{}',
    '•': r'\textbullet{} ',
    '“': '``',
    '”': "''",
    '„': ',,',
    '‘': '`',
    '’': "'",
    '′': "'",
    '″': "''",
    '\u00a0': ' ',
    # Emoji replacements require LuaLaTeX + \usepackage{emoji}.
    '☕': r'\emoji{hot-beverage}',
    '❤': r'\emoji{red-heart}',
    '🌱': r'\emoji{seedling}',
    '🍄': r'\emoji{mushroom}',
    '🍹': r'\emoji{tropical-drink}',
    '🎤': r'\emoji{microphone}',
    '🎨': r'\emoji{artist-palette}',
    '🎶': r'\emoji{musical-notes}',
    '🐮': r'\emoji{cow-face}',
    '💖': r'\emoji{sparkling-heart}',
    '📖': r'\emoji{open-book}',
    '🔥': r'\emoji{fire}',
    '🔮': r'\emoji{crystal-ball}',
    '😂': r'\emoji{face-with-tears-of-joy}',
    '🛠': r'\emoji{hammer-and-wrench}',
    '🛸': r'\emoji{flying-saucer}',
    '🤹': r'\emoji{person-juggling}',
    '🧁': r'\emoji{cupcake}',
    '🧊': r'\emoji{ice}',
    # pink-heart is not available in the TeX emoji package table; degrade gracefully.
    '🩷': r'\emoji{red-heart}',
    # Fallbacks for emojis commonly seen in form exports but unsupported by the font stack.
    '🎱': r'\emoji{pool-8-ball}',
    '😉': ';)',
    '💦': r'\emoji{sweat-droplets}',
    '✨': r'\emoji{sparkles}',
    '🐻': r'\emoji{bear}',
    '🫖': r'\emoji{teapot}',
    # Variation selector in emoji sequences.
    '️': '',
}


LATEX_ESCAPES = {
    '\\': r'\textbackslash{}',
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
}


MAPPED_UNICODE_CHARS = {
    char
    for char in UNICODE_REPLACEMENTS
    if ord(char) > 127
}


def latexize(text):
    """Convert common unicode punctuation and escape LaTeX special chars."""
    if text is None:
        return ''

    normalized = (
        str(text)
        .replace('\r\n', '\n')
        .replace('\r', '\n')
        # Dust/form content often carries literal escape sequences.
        .replace('\\n', '\n')
        .replace('\\t', '    ')
    )

    output = []
    for char in normalized:
        if char in UNICODE_REPLACEMENTS:
            output.append(UNICODE_REPLACEMENTS[char])
        else:
            output.append(LATEX_ESCAPES.get(char, char))
    return ''.join(output)


def collect_non_ascii_chars(value):
    """Return non-ASCII chars that are not already handled by latexize()."""
    if value is None:
        return set()
    return {
        char
        for char in str(value)
        if ord(char) > 127 and char not in MAPPED_UNICODE_CHARS
    }


def report_unicode_warnings(warnings, stream=None):
    """Print a readable warning report for non-ASCII chars."""
    if not warnings:
        return

    stream = stream or sys.stderr
    print(
        '\nUnicode review: non-ASCII characters detected '
        '(may require XeLaTeX/LuaLaTeX or manual cleanup).',
        file=stream,
    )
    for label, chars in warnings:
        char_details = []
        for char in sorted(set(chars)):
            codepoint = f'U+{ord(char):04X}'
            name = unicodedata.name(char, 'UNKNOWN')
            char_details.append(f'{repr(char)} ({codepoint} {name})')
        print(f'  - {label}: {", ".join(char_details)}', file=stream)

