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
# flake8: noqa
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import quote_plus
from urllib.parse import splitvalue
from urllib.parse import unquote
from urllib.parse import unquote_plus
from urllib.parse import urlencode
