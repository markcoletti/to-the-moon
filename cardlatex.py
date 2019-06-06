#!/usr/bin/env python3
"""
    This provides support for generating the LaTeX for waste management postcards.

    Used by csv2postcard.py and db2postcard.py

    E.g.,

        with Path(args.out_file).open('w') as latex_postcards_file:
            cardlatex.write_latex_preamble(latex_postcards_file)

            for viable_violation in viable_violations.values():
                cardlatex.process_violation(viable_violation, latex_postcards_file)

            cardlatex.write_latex_end(latex_postcards_file)

        Where viable_violations is a dictionary of a list of dictionaries.  The outer
        dictionary is keyed by concatenation of "HOUSE #" and "STREET ADDRESS".  The
        lists contains dictionaries that correspond to individual violations, and have
        key names of DATE, OVER FLOW, NOT OUT, NOT AT CURB, and DETAILS.  These values
        ultimately come from either a CSV file or the database.
"""
from string import Template

# TODO Need to use better pythonic string formatting throughout.

# This is maximum number of violations we can handle printing on a postcard before we run out of space
MAX_VIOLATIONS_PRINTED = 4

# This is the maximum number of details we'll allow on a postcard
MAX_DETAILS_PRINTED = 2

postcard_tex_preamble = """\\documentclass[10pt]{article}

\\pagestyle{empty}
\\setlength\\parindent{0pt}
\\usepackage[paperwidth=5in,
    paperheight=3.5in,
    left=0.50in,
    right=0.50in,
    top=0.450in,
    bottom=0.450in]{geometry}

\\usepackage{graphicx}
\\usepackage{enumitem} % for compressed lists
\\usepackage{textpos} % for precise address block placement
\\usepackage{needspace} % try to prevent unnecessary page breaks
\\usepackage{pbox} % for making boxes for the parting lines

% Frantic effort to prevent the "Cordially" lines from occasionally going to another page for no reason.
\\needspace{10\\baselineskip}
\\clubpenalty=10
\\widowpenalties 1 10000
\\raggedbottom

\\renewcommand{\\familydefault}{\\sfdefault} % default font sans serif

\\begin{document}
"""

# This is part of the postcard that contains the violations
violations_tex = """
\\begin{flushleft}
Dear City of Knoxville resident,\\\\[1em]
$violations
$details
\\end{flushleft}
\\vfill
\\pbox{3in}{
Cordially,\\\\[.9em]
Knoxville Solid Waste Management\\\\
{\\tiny http://knoxvilletn.gov/government/city\_departments\_offices/public\_service/solid\_waste}
}
\\hfill
\\pbox{1in}{
\\includegraphics[width=.75in]{knxwasteqrcode}
}
\\newpage
"""

# This is for the address line, of course.
address_tex = """
\\begin{flushleft}
\\includegraphics[width=2in]{knoxlogo}\\\\
Knoxville Solid Waste Management\\\\
400 Main St., Room 470 \\\\
Knoxville, TN 37902
\\end{flushleft}
\\vfill
\\begin{textblock}{3}(5,0)
\\parbox{3in}{\\Large Resident\\\\
$address \\\\
Knoxville, TN 37902}
\\end{textblock}
\\vfill

\\newpage
"""

postcard_tex_end = """
\\end{document}
"""


def write_latex_preamble(out_file):
    """ Write out the preamble, or start, of the LaTeX document that will contain the postcards.

    :param out_file: is the LaTeX that will contain the postcards
    :return: None
    """
    out_file.write(postcard_tex_preamble)


def write_latex_end(out_file):
    """ Write out the end of the LaTeX document for the postcards

    :param out_file: you guessed it, the LaTeX file for the postcards
    :return: None
    """
    out_file.write(postcard_tex_end)


def calculate_violations(violations):
    """
    :param violations: is an OrderedDict for a violation record
    :return: A string summarizing violations
    """

    def is_valid(x):
        """ return false if all three violation fields are blank """
        return x['OVER FLOW'] != '' or x['NOT OUT'] != '' or x['NOT AT CURB'] != ''

    violation_summary = ''

    # Let's filter out the bogus violations where all the violations are blank.
    # TODO we may actually want to whine about such bogus violation records.  :P
    valid_violations = [x for x in violations if is_valid(x)]

    if len(valid_violations) > MAX_VIOLATIONS_PRINTED:
        # These won't all fit on the back of the postcard, so just print the last five, and summarize the total count.
        reported_violations = valid_violations[-MAX_VIOLATIONS_PRINTED:]
        violation_summary += 'We had ' + str(
            len(valid_violations)) + " problems collecting your trash in the period between " + valid_violations[0][
                                 'DATE'] + \
                             ' and ' + valid_violations[-1]['DATE'] + ', and show only the most recent four here.\n\n'
    else:
        reported_violations = valid_violations
        violation_summary += 'We had the following problems collecting your trash:\n'

    violation_summary += '\\begin{itemize}[noitemsep]\n\\scriptsize\n'

    for violation in reported_violations:

        if violation['OVER FLOW'] != '':
            violation_summary += '\\item ' + violation[
                'DATE'] + ' Your trash was overflowing making it difficult to pick-up. \n'

        if violation['NOT OUT'] != '':
            violation_summary += '\\item ' + violation['DATE'] + ' Your trash was not out.  \n'

        if violation['NOT AT CURB'] != '':
            violation_summary += '\\item ' + violation[
                'DATE'] + ' Your trash was not close to the curb, which slowed down pick-up. \n'

    violation_summary += '\\end{itemize} \n'

    return violation_summary


def handle_details(violations):
    """
    :param violations: is an OrderedDict for a violation record
    :return: if there any details, then return them, else return an empty string.
    """
    details = ''

    valid_details = [x for x in violations if x['DETAILS'] != '']

    if valid_details == []:
        # no details, so bail with an empty string indicating no details in any reports for this address
        return details

    if len(valid_details) > MAX_DETAILS_PRINTED:
        details += 'There were more than ' + str(
            MAX_DETAILS_PRINTED) + ' comments for your trash pickup reported in the period ' + \
                   violations[0]['DATE'] + ' and ' + violations[-1]['DATE'] + ', but only report the last two.'
        valid_details = valid_details[-MAX_DETAILS_PRINTED:]
    else:
        details += 'We have the following notes regarding removing your trash:\n'

    details += '\\begin{itemize}[noitemsep]\n\\scriptsize'

    for violation in valid_details:
        if violation['DETAILS'] != '':
            details += '\\item ' + violation['DATE'] + ' ' + violation['DETAILS'] + ' \n'

    details += '\\end{itemize}\n'

    return details


def process_violation(violations, out_file):
    """ This will emit a corresponding postcard for the given violation to the LaTeX postcard file

    :param violations: is an OrderedDict containing details for a specific violation
    :param out_file: is an open connection to the LaTeX file
    :return: None
    """
    # First write out the violations side of the postcard
    violations_string = Template(violations_tex)

    # Get nicely formatted strings for the violations and any driver details to later embed in the postcard.
    violation_summary = calculate_violations(violations)
    details = handle_details(violations)

    out_postcard_string = violations_string.safe_substitute(violations=violation_summary,
                                                            details=details)
    out_file.write(out_postcard_string)

    # Then write the address side of the postcard
    address_string = Template(address_tex)

    # We arbitrarily get the street address from the first violation, violations[0], since all violations
    # *should* have the same address
    out_address_string = address_string.safe_substitute(
        address=violations[0]['HOUSE #'] + ' ' + violations[0]['STREET'])

    # We need to escape hashes, else LaTeX will puke.
    out_address_string = out_address_string.replace('#', '\#')

    out_file.write(out_address_string)

