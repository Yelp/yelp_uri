# -*- coding: utf-8 -*-
"""
A Unicode-friendly wrapper around urllib methods that encodes unicodes into strings.

urlencode(), quote(), and quote_plus() should always be safe replacements for their unwrapped counterparts;
if passed strings, they behave exactly the same.

unquote() and unquote_plus() work just like their unwrapped counterparts, except that they always return unicodes (which
is usually what you want).

The docs for the actual urllib methods are here:
http://docs.python.org/lib/module-urllib.html

WARNING: Despite the fact that this module *supports* having unicode keys in the query
part of a url. YOU SHOULD NOT USE THEM.  That is, you should NEVER support something
like:
BAD: http://www.yelp.com/my_servlet?bäd_param=value

ONLY use ascii for the key in url params.
"""

import urllib
import urlparse

from yelp_bytes import from_utf8, to_utf8


def _pairs(x):
    """If x is a dict, call x.iteritems(), else just return x"""
    return x.iteritems() if isinstance(x, dict) else x


def urlencode(query, *args, **kwargs):
    """A wrapper for urllib.urlencode() that UTF-8 encodes query if
    query is unicode. Always returns a str."""
    return urllib.urlencode([(to_utf8(k), to_utf8(v)) for (k, v) in _pairs(query)], *args, **kwargs)


def quote(string, *args, **kwargs):
    """A wrapper for urllib.quote() that UTF-8 encodes string if
    query is unicode. Always returns a str."""
    """Call urllib.quote(), encoding string in UTF-8 if it's unicode."""
    return urllib.quote(to_utf8(string), *args, **kwargs)


def quote_plus(string, *args, **kwargs):
    """A wrapper for urllib.quote_plus() that UTF-8 encodes string if
    query is unicode. Always returns a str."""
    """Call urllib.quote_plus(), encoding string in UTF-8 if it's unicode."""
    assert isinstance(string, basestring), type(string)
    return urllib.quote_plus(to_utf8(string), *args, **kwargs)


def unquote(s, errors='ignore'):
    """A wrapper for urllib.unquote() that UTF-8 decodes strs.
    Should always return a unicode.

    errors - What to do on a decoding error? Default behavior is
    to ignore bytes that we can't decode."""
    return from_utf8(urllib.unquote(to_utf8(s)), errors=errors)


def unquote_plus(s, errors='ignore'):
    """A wrapper for urllib.unquote_plus() that UTF-8 decodes strs.
    Should always return a unicode.

    errors - What to do on a decoding error? Default behavior is
    to ignore bytes that we can't decode."""
    return from_utf8(urllib.unquote_plus(to_utf8(s)), errors=errors)


def splitvalue(s):
    return urllib.splitvalue(to_utf8(s))


def parse_qs(query_string, errors='ignore'):
    """Wrap urlparse.parse_qs() to handle URL-encoded strings stored in class unicode and similar travesties."""
    # Actually from urlparse, not urllib; might get its own urlparse_utf8.py some day.
    kwargs_bytes = urlparse.parse_qs(to_utf8(query_string))
    kwargs = dict((
        (
            key,
            [from_utf8(value, errors=errors) for value in value_list],
        )
        for key, value_list in kwargs_bytes.iteritems()
    ))
    return kwargs
