from markupsafe import Markup
from yelp_uri.linkify import linkify


def test_linkify():

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
