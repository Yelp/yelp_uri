from yelp_uri.search import url_regex_common_tlds
from yelp_uri.encoding import decode_uri
from yelp_uri.encoding import encode_uri


def create_link(uri, markup_class):
    text = decode_uri(uri)
    uri = encode_uri(uri)

    if not uri.startswith('http://') and not uri.startswith('https://'):
        uri = 'http://' + uri
    return markup_class('<a href="{uri}">{text}</a>').format(uri=uri, text=text)


def linkify(text, markup_class):
    result = []
    prev_end = 0
    for match in url_regex_common_tlds.finditer(text):
        result.append(text[prev_end:match.start()])
        result.append(create_link(match.group(), markup_class))
        prev_end = match.end()
    result.append(text[prev_end:])

    return markup_class().join(result)
