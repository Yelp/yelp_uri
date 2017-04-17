import re

from yelp_uri.search import url_regex_common_tlds
from yelp_uri.encoding import decode_uri
from yelp_uri.encoding import encode_uri


def split_linenumber(uri_match):
    '''Split uri into two parts: the actual uri and the line number'''

    path_query_fragment = uri_match.group('path_query_fragment')
    line_number = ''
    if path_query_fragment is not None:
        _, line_number = re.match(r'^(.+?)((?::\d+)*)$', path_query_fragment).groups('')

    if len(line_number) == 0:
        url = uri_match.group()
    else:
        # Strip trailing line numbers
        url = uri_match.group()[:-len(line_number)]

    return url, line_number


def create_link(uri_match, markup_class):
    '''Create a html link that is markup safe.'''

    uri, rest = split_linenumber(uri_match)

    text = decode_uri(uri)
    uri = encode_uri(uri)

    if not uri.startswith('http://') and not uri.startswith('https://'):
        uri = 'http://' + uri
    return markup_class('<a href="{uri}">{text}</a>{rest}').format(uri=uri, text=text, rest=rest)


def linkify(text, markup_class, regex=url_regex_common_tlds):
    '''Change every uri in a string into a html link. Return a markup safe string that is ready to be used in html.'''

    result = []
    prev_end = 0
    for match in regex.finditer(text):
        result.append(text[prev_end:match.start()])
        result.append(create_link(match, markup_class))
        prev_end = match.end()
    result.append(text[prev_end:])

    return markup_class().join(result)
