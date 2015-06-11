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
import six

if six.PY3:
    # Python3 supports all of these out of the box
    # pylint: disable=unused-import,no-name-in-module,import-error
    from urllib.parse import parse_qs
    from urllib.parse import quote
    from urllib.parse import quote_plus
    from urllib.parse import splitvalue
    from urllib.parse import unquote
    from urllib.parse import unquote_plus
    from urllib.parse import urlencode
else:
    urlparse = six.moves.urllib.parse

    from yelp_bytes import from_utf8, to_utf8

    def _pairs(obj):
        """If obj is a dict, call obj.items(), else just return obj"""
        return obj.items() if isinstance(obj, dict) else obj

    def urlencode(query, doseq=0):
        """A wrapper for urllib.urlencode() that UTF-8 encodes query if
        query is unicode. Always returns a str."""
        # see: https://github.com/python/cpython/blob/2.7/Lib/urllib.py#L1340
        def encode_pair(key, val):
            if doseq and isinstance(val, (list, tuple)):
                return to_utf8(key), [to_utf8(item) for item in val]
            else:
                return to_utf8(key), to_utf8(val)

        return urlparse.urlencode([encode_pair(k, v) for (k, v) in _pairs(query)], doseq=doseq)

    def quote(string, *args, **kwargs):
        """A wrapper for urllib.quote() that UTF-8 encodes string if
        query is unicode. Always returns a str."""
        return urlparse.quote(to_utf8(string), *args, **kwargs)

    def quote_plus(string, *args, **kwargs):
        """A wrapper for urllib.quote_plus() that UTF-8 encodes string if
        query is unicode. Always returns a str."""
        assert isinstance(string, six.string_types), type(string)
        return urlparse.quote_plus(to_utf8(string), *args, **kwargs)

    def unquote(string, errors='ignore'):
        """A wrapper for urllib.unquote() that UTF-8 decodes strs.
        Should always return a unicode.

        errors - What to do on a decoding error? Default behavior is
        to ignore bytes that we can't decode."""
        return from_utf8(urlparse.unquote(to_utf8(string)), errors=errors)

    def unquote_plus(string, errors='ignore'):
        """A wrapper for urllib.unquote_plus() that UTF-8 decodes strs.
        Should always return a unicode.

        errors - What to do on a decoding error? Default behavior is
        to ignore bytes that we can't decode."""
        return from_utf8(urlparse.unquote_plus(to_utf8(string)), errors=errors)

    def splitvalue(string):
        return urlparse.splitvalue(to_utf8(string))

    def parse_qs(query_string, errors='ignore'):
        """Wrap urlparse.parse_qs() to handle URL-encoded strings stored in class unicode and similar travesties."""
        # Actually from urlparse, not urllib; might get its own urlparse_utf8.py some day.
        kwargs_bytes = urlparse.parse_qs(to_utf8(query_string))
        kwargs = dict((
            (
                key,
                [from_utf8(value, errors=errors) for value in value_list],
            )
            for key, value_list in kwargs_bytes.items()
        ))
        return kwargs
