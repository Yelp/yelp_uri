from markupsafe import Markup
from yelp_uri.linkify import linkify


def test_linkify():
    '''Test that all uris in a string are wrapped as html links and remaining text is markup safe.'''

    plaintext = '''
        no xss here: <script>alert('hax')</script>
        Reference: http://en.wikipedia.org/wiki/Eon_(geology)
        Follow @YelpCincy on Twitter (http://twitter.com/YelpCincy)
        Don't forget about example.com
    '''

    linkified = linkify(plaintext, Markup)

    assert linkified == '''
        no xss here: &lt;script&gt;alert(&#39;hax&#39;)&lt;/script&gt;
        Reference: <a href="http://en.wikipedia.org/wiki/Eon_(geology)">http://en.wikipedia.org/wiki/Eon_(geology)</a>
        Follow @YelpCincy on Twitter (<a href="http://twitter.com/YelpCincy">http://twitter.com/YelpCincy</a>)
        Don&#39;t forget about <a href="http://example.com">example.com</a>
    '''


def test_uri_line_numbers():
    '''Test that uri with line numbers (javascript stacktraces, for example) do not include the line numbers in link.'''

    plaintext = '''
        Error at line: http://example.com/cleanup_hooks.js?param:73:45
        Many line/column numbers http://example.com/file.js:12:34:56:78
        uri with port and no path: www.example.com:8080:100
        uri with port and path: http://example.com:8080/file.js:100
        Exception message, details in parens (http://example.com/buggy_file.js:3000)
    '''

    linkified = linkify(plaintext, Markup)

    assert linkified == '''
        Error at line: <a href="http://example.com/cleanup_hooks.js?param">http://example.com/cleanup_hooks.js?param</a>:73:45
        Many line/column numbers <a href="http://example.com/file.js">http://example.com/file.js</a>:12:34:56:78
        uri with port and no path: <a href="http://www.example.com:8080">www.example.com:8080</a>:100
        uri with port and path: <a href="http://example.com:8080/file.js">http://example.com:8080/file.js</a>:100
        Exception message, details in parens (<a href="http://example.com/buggy_file.js">http://example.com/buggy_file.js</a>:3000)
    '''
