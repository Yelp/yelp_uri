# -*- coding: utf-8 -*-
"""Handle encoding of uris.

This is complicated since a uri consists of several parts with non-uniform encoding schemes.
In general, hostnames should be punycode, usernames should be utf8, and everything else should be urlquote+utf8.
"""
import re

import six
quote = six.moves.urllib.parse.quote

from yelp_uri import urlsplit, urlunsplit, RFC3986, MalformedUrlError, SplitResult
from yelp_bytes import from_bytes
from yelp_bytes import to_bytes


def encode_uri(uri):
    """Given a (presumed decoded) uri, return a well-encoded uri suitable for an html href."""
    uri = urlsplit(uri)

    new_uri = encode_split_uri(uri)

    return urlunsplit(new_uri)


def encode_split_uri(uri):
    """uri -- a yelp.uri.SplitResult object"""
    return SplitResult(
        _encode(uri.scheme),
        _encode(uri.username, expected=RFC3986.userinfo),
        _encode(uri.password, expected=RFC3986.userinfo),
        _encode_hostname(uri.hostname),
        _encode(uri.port, encoding='ASCII', expected=RFC3986.digits),
        _encode(uri.path, expected=RFC3986.path),
        _encode(uri.query, expected=RFC3986.query),
        _encode(uri.fragment, expected=RFC3986.fragment),
    )


def decode_uri(uri):
    """Given a uri, return a decoded uri suitable for displaying to users."""
    uri = urlsplit(uri)

    new_uri = decode_split_uri(uri)

    return urlunsplit(new_uri)


def decode_split_uri(uri):
    """uri -- a yelp.uri.SplitResult object"""
    return SplitResult(
        _decode(uri.scheme),
        _decode(uri.username),
        _decode(uri.password),
        _decode_hostname(uri.hostname),  # Decoded below
        _decode(uri.port, encoding='ASCII'),
        _decode(uri.path),
        _decode(uri.query),
        _decode(uri.fragment),
    )


def recode_uri(uri):
    """Take an unknown uri and return a well-encoded uri suitable for an html href.
    This is essentially equivalent to encode(decode(uri)), but a little more efficient.
    """
    uri = urlsplit(uri)

    new_uri = recode_split_uri(uri)

    return urlunsplit(new_uri)


def recode_split_uri(uri):
    """uri -- a yelp.uri.SplitResult object"""
    return encode_split_uri(decode_split_uri(uri))


def encode_email(email):
    email = _emailsplit(email)

    new_email = encode_split_email(email)

    return _emailunsplit(new_email)


def encode_split_email(email):
    """email -- a yelp.uri.SplitResult object"""
    return SplitResult(
        _encode(email.scheme),  # Could be "mailto"
        # We can't percent-quote email usernames because of the postfix "percent hack"
        # http://www.postfix.org/postconf.5.html#allow_percent_hack
        _encode(email.username, expected=RFC3986.userinfo, encoding=None),
        None,  # Passwords are invalid.
        _encode_hostname(email.hostname),
        None,  # Ports are invalid.
        None,  # Paths are invalid.
        _encode(email.query, expected=RFC3986.query),  # Subject and body could be here.
        None,  # Fragments are invalid
    )


def decode_email(email):
    email = _emailsplit(email)

    new_email = decode_split_uri(email)

    return _emailunsplit(new_email)


def decode_split_email(email):
    """email -- a yelp.email.SplitResult object"""
    return SplitResult(
        _decode(email.scheme),  # Could be "mailto"
        _decode(email.username),
        None,
        _decode_hostname(email.hostname),  # Decoded below
        None,
        None,
        _decode(email.query),  # Subject and body could be here.
        None,
    )


def recode_email(email):
    email = _emailsplit(email)

    new_email = recode_split_email(email)

    return _emailunsplit(new_email)


def recode_split_email(email):
    """email -- a yelp.uri.SplitResult object"""
    return encode_split_email(decode_split_email(email))


# Helper functions, not for export. #


def _encode(string, encoding='UTF-8', expected='', quoted=True):
    if string is None:
        return string
    string = from_bytes(string)

    if encoding:
        string = string.encode(encoding)
        if quoted:
            string = quote(string, expected)
        else:
            string = string.decode('ASCII')

    return string


def _encode_hostname(hostname):
    # Fix-up bad leading/trailing/consecutive dots in the domain
    # -- prior art in chromium browser.
    if hostname is None:
        return hostname

    hostname = hostname.strip('.')
    hostname = _extra_dots_RE.sub('.', hostname)
    try:
        # Because IDNA should always return ascii, there should be no percent-quotes in the hostnames after encoding.
        return _encode(hostname, encoding='IDNA', quoted=False)
    except UnicodeError as error:
        # Make this error a little more explicit and catch-able.
        if len(error.args) == 1 and isinstance(error.args[0], str):
            raise MalformedUrlError('Invalid hostname: %s: %r' % (error.args[0], hostname))
        else:  # An exception I don't expect
            raise


def _decode_hostname(hostname):
    # IDNA decoding is not idempotent (sadface) so we need a special case here.
    if hostname is None:
        return hostname

    hostname = to_bytes(hostname)
    hostname = _unquote_bytes(hostname)
    if _is_punycoded(hostname):
        return hostname.decode('IDNA')
    else:
        return hostname.decode('internet')


def _decode(string, encoding='internet'):
    if string is None:
        return string
    string = to_bytes(string)
    string = _unquote_bytes(string)
    string = string.decode(encoding)
    return string


_ascii_plaintext = RFC3986.plaintext.encode('US-ASCII')


def _unquote_bytes(string):
    """Similar to urllib.unquote, but only unquote ASCII-plaintext and non-ASCII bytes (0x80-0xFF).
    This is only for use by _decode(), above.
    """

    res = string.split(b'%')
    for i in range(1, len(res)):
        item = res[i]
        try:
            c = int(item[:2], 16)
        except ValueError:
            res[i] = b'%' + item
        else:
            char = six.int2byte(c)
            if (
                    c >= 0x80 or
                    char in _ascii_plaintext
            ):
                res[i] = char + item[2:]
            else:
                res[i] = b'%' + item
    return b''.join(res)


_extra_dots_RE = re.compile(r'\.\.+')


def _is_punycoded(domain):
    """Hackity check to see if domain has been IDNA-encoded (aka punycode)
    It's essentially what the idna codec does internally though.
    """
    from encodings.idna import ace_prefix

    return any(label.startswith(ace_prefix) for label in domain.split(b'.'))


def _emailsplit(email):
    """We don't support the full RFC6068 here, just a single email.
    To simplify processing, we treat the email as a username@hostname,
    rather than uri-path as specified.

    This is rather hackity. To do it the Right Way would probably necessitate a whole new namespace.
    """
    email = urlsplit(email)

    if email.path:
        username, sep, hostname = email.path.rpartition('@')
        if not sep:
            username = None
        return email.replace(username=username, hostname=hostname, path='')
    else:
        return email


def _emailunsplit(split_email):
    """Given a result from _emailsplit, return an email string."""
    # I know. Gross. I don't see a better way.
    email_path = '@'.join(s for s in (split_email.username, split_email.hostname) if s is not None)
    split_email = split_email.replace(username=None, hostname=None, path=email_path)
    return urlunsplit(split_email)
