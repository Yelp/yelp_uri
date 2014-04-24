#!/usr/bin/python
# -*- coding: utf-8 -*-
_suites = ['unicode']

import urllib
import urlparse

from yelp_uri import urllib_utf8


def test_urlencode():
    query = {
        'empty': '',  # empty string
        'x': 'y',  # normal ASCII
        'foo': u'bär',  # unicode val
        u'bärge': 'large',  # unicode key
        u'äah': 'yätes',  # unicode key & val
        # a non-ASCII str, just to make things interesting
        'name': 'Unique Caf\xe9',
    }

    # the same query, as utf-8 encoded strings
    utf8_query = dict(
        (k.encode('utf-8'), v.encode('utf-8') if isinstance(v, unicode) else v)
        for (k, v) in query.iteritems()
    )

    # Dictionaries can re-order the url params, so we
    # compare the split up params as sets
    def assert_params_equal(left, right):
        assert set(left.split('&')) == set(right.split('&'))

    assert_params_equal(urllib_utf8.urlencode(query),
                        urllib.urlencode(utf8_query))

    # try again, but with arrays of pairs
    assert_params_equal(urllib_utf8.urlencode(query.items()),
                        urllib.urlencode(utf8_query))


def test_quote_and_quote_plus():

    strings = ['', 'Hello there!', u'naïve', u' San José ', ' cafés']
    for string in strings:
        utf8_string = string.encode('utf-8') if isinstance(string, unicode) else string
        assert urllib_utf8.quote(string) == urllib.quote(utf8_string)
        assert urllib_utf8.quote_plus(string) == urllib.quote_plus(utf8_string)


def test_quote_unicode():
    """Quoting and unquoting Unicode strings should give the same result
    as when given regular strings. See ticket #28786.
    """
    assert urllib_utf8.quote('montréal') == urllib_utf8.quote(u'montréal')
    assert urllib_utf8.quote_plus('montréal') == urllib_utf8.quote_plus(u'montréal')
    assert urllib_utf8.unquote('montréal') == urllib_utf8.unquote(u'montréal')
    assert urllib_utf8.unquote_plus('montréal') == urllib_utf8.unquote_plus(u'montréal')


def test_parse_qs():
    """urllib_utf8.parse_qs should mostly act like urlparse.parse_qs."""
    strings = ['', 'foo=bar', u'foo=bar', 'foo=bar&baz=quux', 'foo=1&foo=2']
    for query_string in strings:
        assert urllib_utf8.parse_qs(query_string) == urlparse.parse_qs(query_string)
        utf8_string = query_string.encode('utf-8') if isinstance(query_string, unicode) else query_string
        assert urllib_utf8.parse_qs(query_string) == urlparse.parse_qs(utf8_string)
        assert urllib_utf8.parse_qs(query_string) == urlparse.parse_qs(utf8_string)


def _verify_extract_unicode_value(query_string, expected_value):
    """Verify the first 'foo=X' value matches expected_value."""
    kwargs = urllib_utf8.parse_qs(query_string)
    assert kwargs['foo'][0] == expected_value


def test_parse_qs_unicode():
    """Our Tornado 1 setup sometimes gives URL-encoded strings as (byte)strings as expected.
    Verify we can properly handle this case, and give proper Unicode output.
    """
    _verify_extract_unicode_value('foo=M%C3%BCnchen', u'München')


def test_parse_qs_mangled():
    """Our Tornado 2 setup sometimes gives URL-encoded strings in the Unicode, rather than (byte)string,
    class.  Normal urlparse.parse_qs does an implicit decoding as latin1 or some similar goofiness,
    mangling any non-ASCII.  Verify we can properly handle this case, and give proper Unicode output.
    """
    _verify_extract_unicode_value(u'foo=M%C3%BCnchen', u'München')
