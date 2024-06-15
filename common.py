#!/usr/bin/env python3
"""
    Contains common functions and variables used by multiple scripts.
"""
def latexize(text):
    """ Escape all LaTeX hostile characters

    :param text: contains text that may contain LaTeX unfriendly characters.
    :return: text with strings properly escaped
    """
    return text.replace('&','\\&').replace('#','\\#').replace('{','\\{').replace('}','\\}').replace('_','\\_')

