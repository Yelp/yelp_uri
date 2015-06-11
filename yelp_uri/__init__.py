# -*- coding: utf-8 -*-
"""
The python standard library is a bit deficient in its handling of urls.
This namespace contains the yelp extensions to the stdlib functionality.

This understanding of urls is based on RFC3986: http://www.ietf.org/rfc/rfc2396.txt
Where RFC3986 is incompatible with RFC2396 (the older, obsoleted standard), we prefer strict compatibility with RFC3986.

Because email addresses resemble uris in several regards, we handle them under this namespace as well.
"""
# This namespace reserved for *very* general-purpse uri functions.

import re
try:
    from string import ascii_letters as LETTERS
except ImportError:
    from string import letters as LETTERS  # pylint: disable=no-name-in-module
from string import digits as DIGITS, printable as PRINTABLE
from collections import namedtuple

import six
from yelp_bytes import from_bytes

import yelp_uri._urlparse_less_special as _urlparse


class MalformedUrlError(UnicodeError):
    """This error means there are unrecoverable issues with your url"""
    # I derive from UnicodeError because that's what the IDNA encoder throws with a bad domain name.
    # Also, UnicodeError derives from ValueError, which is what urlparse throws with a non-numeric port.
    pass


class RFC3986(object):  # pylint:disable=too-many-instance-attributes
    """
    Codify some knowlege about the characters in a URL
    From:
        http://tools.ietf.org/html/rfc3986#appendix-A

    This class has an 're' attribute which holds values suitable for inclusion
    in a regular expression.
    """

    def __init__(self):
        # Basic character classes, useful later.
        self.digits = DIGITS
        self.letters = LETTERS
        self.alphanum = DIGITS + LETTERS
        self.whitespace = re.search(r'\s+', PRINTABLE).group()

        # From http://tools.ietf.org/html/rfc3986#appendix-A
        # In reverse order:
        self.subdelims = "!$&'()*+,;="
        self.gendelims = ':/?#@'
        self.reserved = self.subdelims + self.gendelims
        # Combined: Wherever unreserved is used, percent-encoded is as well.
        self.unreserved = self.alphanum + '-._~' + '%'
        self.pchar = self.unreserved + self.subdelims + ':@'
        self.query = self.pchar + '/?'
        self.fragment = self.pchar + '/?'
        self.path = self.pchar + '/'
        # deviation: The "subdelims" actually don't make sense in domain names or user names
        self.regname = self.unreserved
        self.userinfo = self.unreserved + '+'

        # Yelp extension: characters that don't belong at the end of a URI
        self.bad_end = self.whitespace + '''<(.!'",;?:-'''
        # The set of characters that is always OK to unescape.
        self.plaintext = self.alphanum + '_-'
        # The set of allowable URL characters.
        self.url = self.unreserved + self.reserved

        self.re = self.produce_character_classes()  # pylint:disable=invalid-name

    def produce_character_classes(self):
        class RFC3986re(object):
            pass

        for attr, val in vars(self).items():
            re_val = re.escape(val)
            re_val = re.sub('[^' + re_val + ']', '', PRINTABLE)
            re_val = self.norm_re_class(re_val)
            # print '%20s : %s' % (attr, re_val)
            setattr(RFC3986re, attr, re_val)

            neg_attr = 'not_' + attr
            neg_val = re.sub('[' + re_val + ']', '', PRINTABLE)
            neg_val = self.norm_re_class(neg_val)
            # print '%20s : %s' % (neg_attr, neg_val)
            setattr(RFC3986re, neg_attr, neg_val)

        return RFC3986re

    def norm_re_class(self, re_class):
        re_class = re_class.replace(self.whitespace, 'space')
        if '_' in re_class and self.alphanum in re_class:
            re_class = re_class.replace(self.alphanum, 'word').replace(r'\_', '')
        return re.escape(re_class).replace('space', r'\s').replace('word', r'\w')

# This is a singleton class
RFC3986 = RFC3986()


def netlocsplit(netloc):
    "Split a `netloc` into its component parts."
    # Leverage the code already implemented in urlparse.ResultMixin
    tmp = _urlparse.ResultMixin()
    tmp.netloc = netloc
    try:
        port = tmp.port
    except ValueError as error:
        # Make this error a little more explicit and catch-able.
        if len(error.args) == 1 and isinstance(error.args[0], str):
            raise MalformedUrlError('Invalid port number: ' + error.args[0])
        else:  # An exception I don't expect
            raise

    return NetlocSplitResult(tmp.username, tmp.password, tmp.hostname, port)


def netlocunsplit(split_netloc):
    "Given a result from `netlocsplit`, return a string that would `netlocsplit` into the same tuple."
    user, passwd, host, port = split_netloc

    netloc = host
    if port is not None:
        netloc = netloc + ':' + str(port)
    if user is not None or passwd is not None:
        netloc = '@' + netloc
        if passwd is not None:
            netloc = ':' + passwd + netloc
        if user is not None:
            netloc = user + netloc

    return netloc


class NetlocSplitResult(namedtuple('NetlocSplitResult', 'username password hostname port')):
    """A result from yelp.uri.netlocsplit
    See also: /usr/lib/python2.6/urlparse.py:SplitResult
    """

    __slots__ = ()

    def geturl(self):
        return netlocunsplit(self)


def urlsplit(url):
    """Similar to stdlib urlparse.urlsplit, but splits the url into more parts.

    url -- string url to be parsed.
    return -- a yelp.uri.SplitResult
    """
    url = _urlparse.urlsplit(
        from_bytes(url) if isinstance(url, six.binary_type) else url
    )
    nl = netlocsplit(url.netloc)
    return SplitResult(url.scheme, nl.username, nl.password, nl.hostname, nl.port, url.path, url.query, url.fragment)


def urlunsplit(split_url):
    """"
    split_url -- a yelp.uri.SplitResult
    return -- url string
    """
    netloc = netlocunsplit(split_url[1:5])

    split_url2 = list(split_url)
    split_url2[1:5] = [netloc]
    return _urlparse.urlunsplit(split_url2)


class SplitResult(namedtuple('SplitResult', 'scheme username password hostname port path query fragment')):
    """A result from yelp.uri.urlsplit
    See also: /usr/lib/python2.6/urlparse.py:SplitResult
    """

    __slots__ = ()

    def geturl(self):
        return urlunsplit(self)

    @property
    def netloc(self):
        return NetlocSplitResult(self.username, self.password, self.hostname, self.port)

    def replace(self, **kwargs):
        """_replace has been promoted to a public method"""
        return self._replace(**kwargs)


# List the names that this module "really" exports.
__all__ = (
    'RFC3986',
    'netlocsplit',
    'netlocunsplit',
    'NetlocSplitResult',
    'urlsplit',
    'urlunsplit',
    'SplitResult',
)
