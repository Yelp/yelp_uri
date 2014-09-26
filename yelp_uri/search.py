# -*- coding: utf-8 -*-
import re

from yelp_uri import RFC3986
from .tlds import tlds

# A regex for finding urls in free-form text.
# This regex is space-indented, so that it looks OK on ReviewBoard
#
# the following regex works like this:
# first part of URL is either:
#   http:// or https:// followed by any dotted hostname
#    or
#   dotted hostname where last part is com, net, org, etc. (so we don't accidentally linkify wrong stuff)
#    and in this case, the hostname cannot be preceded by dot or @ (or alphanum), as this causes weird matches
#
# (optional) second part of URL can consist of lots of differrent characters,
#  but cannot end in .!,?;:( because those are maybe not meant to be part of the URL.
# NOTE: regex has been recently modified to allow a url to end in ")" so it can support urls
# that contain parenthesis, such as wikipedia urls (e.g. 'http://en.wikipedia.org/wiki/Ham_(disambiguation)')
# linkify_url has also been changed to look for urls ending in a ")" that do not have a matching "(", and moves
# it outside of the closing link tag if found.
url_regex = re.compile(
    r"""
        # Don't start in the middle of something.
        (?<!  [\w.@/:-] )
        (?!  mailto: )
        # Looking for a domain name
        (
            # we look for a known prefix
            (
                https?://
            |
                www\.
            )
            ([^%(not_userinfo)s]+@)? # maybe a user?
            [^%(not_regname)s]+
            \.
            [^%(not_regname)s.]{2,}
            (:\d+)? # maybe a port?
        |
            # or else look for a domain name with a known suffix.
            # We're more strict about dots / userinfo in this case, since the
            # user intent is more ambiguous.
            (   # one or more domain segments
                [^%(not_regname)s.]+\.
            )+
            (%(tlds)s)
            (:\d+)? # maybe a port?
        )
        # An optional path/query/fragment component
        (
            [/?#]
            (
                # Figure out if we have parens in our url
                (?=(?P<HAS_PARENS>
                    [^:%(not_url)s]*\(
                ))?
                (?(HAS_PARENS)
                    # If we have parens, we use this:
                    [^%(not_url)s]*
                    [^%(bad_end)s]
                |
                    # Otherwise, we use this:
                    [^\)%(not_url)s]*
                    [^\)%(bad_end)s]
                )
            )?
        )?
        # Look-ahead to make sure the URL ends nicely.
        (?=
            [\)%(bad_end)s]
        |
            $
        )
    """ % dict(
        vars(RFC3986.re),
        tlds=tlds,
    ),
    re.VERBOSE | re.UNICODE | re.IGNORECASE,
)


# A regex for finding email addresses in free-form text.
email_regex = re.compile(
    r"""
        (?: # Don't start in the middle of something.
            (?<!  [\w.@/:-] )
            |
            (?<= mailto:// )
        )
        (   # A local-part in an email address
            # Can't have percent signs. See: http://www.postfix.org/postconf.5.html#allow_percent_hack
            [^%(not_userinfo)s%%]+
        )
        @ # At sign
        ( # Start of FQDN
            (?: # one or more domain segments
                [^%(not_regname)s.]+\.
            )+
            [^%(not_regname)s.]{2,} # Top-level domain
        ) # End of FQDN
    """ % vars(RFC3986.re),
    re.VERBOSE | re.UNICODE
)

# List the names that this module "really" exports.
__all__ = (
    'url_regex',
    'email_regex',
)
# vim:et:sts=4
