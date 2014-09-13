from __future__ import print_function
import sys
import urllib2


"""
This reads the IANA-maintained list of tlds and formats/outputs them for use
in the domains regular expression. All you have to do is replace the 
existing "domains = ..." line in search.py with this script's output.
"""


def main(url='http://data.iana.org/TLD/tlds-alpha-by-domain.txt'):
    try:
        domain_data = urllib2.urlopen(url)
    except URLError as e:
        print(
            "Could not get the domains from the given URL. Perhaps the IANA"
            "has changed the location of the file or it no longer exists."
        )
        return e.reason

    # Convert all newlines except the last one to '|', so 'foo\nbar\n' -> 'foo|bar'.
    # Ignores all lines starting with '#', which is a comment in the text file.
    domains_string = '|'.join(
        line.lower() for line in domain_data.read().splitlines()
        if not line.startswith("#") and line.strip()
    )

    print('domains = r"{0}"  # NOQA'.format(domains_string))


if __name__ == "__main__":
    sys.exit(main())
