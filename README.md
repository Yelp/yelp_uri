# yelp\_uri

[![Build Status](https://travis-ci.org/Yelp/yelp_uri.svg)](https://travis-ci.org/Yelp/yelp\_uri)


## Installation

For a primer on pip and virtualenv, see the [Python Packaging User Guide](https://python-packaging-user-guide.readthedocs.org/en/latest/tutorial.html).

TL;DR: `pip install yelp_uri`


## Usage

Make a well-encoded URI from user input.

```python
    >>> weird_uri = 'http://münch.com/münch?one=m%C3%BCnch#m%FCnch'

    >>> import yelp_uri.encoding as E
    >>> well_encoded = E.recode_uri(weird_uri)
    >>> print(well_encoded)
    http://xn--mnch-0ra.com/m%C3%BCnch?one=m%C3%BCnch#m%C3%BCnch

```

Make a user-readable url, from either a well-encoded url or user input:

```python
    >>> print(E.decode_uri(well_encoded))
    http://münch.com/münch?one=münch#münch
    >>> print(E.decode_uri(weird_uri))
    http://münch.com/münch?one=münch#münch

```



`yelp_uri.search` has regexes for finding URLs in user-generated plaintext.

```python
    >>> plaintext = '''
    ...     Reference: http://en.wikipedia.org/wiki/Eon_(geology)
    ...     Follow @YelpCincy on Twitter (http://twitter.com/YelpCincy)
    ... '''
    >>> from yelp_uri.search import url_regex
    >>> for url in url_regex.finditer(plaintext): print(url.group())
    http://en.wikipedia.org/wiki/Eon_(geology)
    http://twitter.com/YelpCincy

```
