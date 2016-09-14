# -*- coding: utf-8 -*-
import six

from yelp_uri.search import email_regex
from yelp_uri.search import url_regex
from yelp_uri.search import url_regex_common_tlds


def test_email_regex():
    """Test that our email-matching regex and fast url/email matching regex work properly."""

    def assert_finds_email(text, email=None):
        if email is None:
            email = text
        match = email_regex.search(text)
        assert match
        user, domain = match.groups()
        assert '%s@%s' % (user, domain) == email

    def assert_no_email(text):
        assert not email_regex.search(text)

    assert_finds_email('i_love_yelp@yahoo.com')
    assert_finds_email('Tom+Yelp@yahoo.com')
    assert_finds_email('info@te-aro.ca')
    assert_finds_email(u'Soirée@yelp.com')
    if not six.PY3:  # Regexes aren't valid for both bytes and str in py3
        assert_finds_email(u'Soirée@yelp.com'.encode('utf8'))
    assert_finds_email('"Tom H" <Tom@yahoo.com>', 'Tom@yahoo.com')
    assert_finds_email('Email me at dave@yelp.com.', 'dave@yelp.com')
    assert_finds_email(
        'john.c.lilly@sensorydeprivation.co.uk is the person to talk to',
        'john.c.lilly@sensorydeprivation.co.uk',
    )
    assert_finds_email('"John Q. Public" <john.q.@gmail.com>', 'john.q.@gmail.com')  # Username ends in "."
    assert_no_email('Read http://www.girlgeniusonline.com')
    assert_no_email('br@n is the @wesome!!!')
    assert_no_email('http://user@example.com:8080?query!')
    assert_no_email('Log in with http://guest@example.com...')


class RegexAssertion(object):
    def __init__(self, url_regex):
        self.url_regex = url_regex

    def assert_finds_url(self, text, url):
        match = self.url_regex.search(text)
        assert match is not None, "Expected url_regex match on " + url + " (text: '" + text + "')"
        assert match.group() == url

    def assert_finds_whole_url(self, url):
        self.assert_finds_url(url, url)

    def assert_no_url(self, text):
        assert self.url_regex.match(text) is None


def assert_url_regex(a):

    a.assert_finds_url('dictionary.com\'s', 'dictionary.com')
    a.assert_finds_url('yelp.com.', 'yelp.com')
    a.assert_finds_url('http://sensorydeprivation.co.uk is the person to talk to', 'http://sensorydeprivation.co.uk')
    a.assert_finds_url('Read https://www.girlgeniusonline.com', 'https://www.girlgeniusonline.com')
    a.assert_finds_url('look at this site with com in it: http://news.ycombinator.com', 'http://news.ycombinator.com')
    a.assert_finds_url('My site is http://example.com.I am bad at spacebar.', 'http://example.com')
    a.assert_finds_url('Check out http://I.have.com?query!', 'http://I.have.com?query')
    a.assert_finds_url('Check out http://I.have.com#!she/bang!', 'http://I.have.com#!she/bang')
    a.assert_finds_url('Follow @YelpCincy on Twitter (http://twitter.com/YelpCincy)', 'http://twitter.com/YelpCincy')
    a.assert_finds_url(
        'Reference: http://en.wikipedia.org/wiki/Eon_(geology)',
        'http://en.wikipedia.org/wiki/Eon_(geology)',
    )
    a.assert_finds_url('http://example.com:8O80', 'http://example.com')
    a.assert_finds_url('notemail@https://example.com', 'https://example.com')
    a.assert_finds_url('notemail@www.example.com', 'www.example.com')

    a.assert_finds_whole_url('http://example.com:8080')
    a.assert_finds_whole_url('http://lil_jay78.blogspot.com/')
    a.assert_finds_whole_url('http://yelp.com/berkeley')
    a.assert_finds_whole_url('www.audrey_tsang.com')
    a.assert_finds_whole_url('http://a.com')
    a.assert_finds_whole_url('http://who_even_uses_dot_mobi.mobi')
    a.assert_finds_whole_url(u'http://www.yelp.com/münchen')
    a.assert_finds_whole_url(u'http://www.ü.com/ü;ü;ü/ü;ü;ü?ü=ü&ü=ü#!ü/ü')
    a.assert_finds_whole_url(u'http://➡.ws/➡;➡;➡/➡;➡;➡?➡=➡&➡=➡#!➡/➡')
    a.assert_finds_whole_url('http://y.combinator')
    a.assert_finds_whole_url('http://.ocregion.com')

    # Chops off everything after last tld, www.dmv.ca
    a.assert_finds_url('https://www.dmv.ca.gov\\notpartofurl', 'https://www.dmv.ca.gov')
    # Chops off path after www.dmv.ca
    a.assert_finds_url(
        'Contact the dmv: https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus\\nnext_paragraph',
        'https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus'
    )
    # Chops off path at the last period, which is the last bad_end
    a.assert_finds_url(
        'Contact the dmv: https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus.html\\nnext_paragraph',
        'https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus.html'
    )
    # :39 is a line number in this context but is valid path component
    a.assert_finds_whole_url('https://media4.com/en_US.min.js:39')
    # Proves :39 is indeed the path component and not the port
    a.assert_finds_whole_url('https://media4.com:443/en_US.min.js:39')

    # Ticket: #31242
    colon_url = 'http://www.yelp.fr/biz/smalls-marseille#hrid:u_UQvMf97E8pD4HEb59uIw'
    a.assert_finds_whole_url(colon_url)
    a.assert_finds_url('(%s)' % colon_url, colon_url)
    colon_url_with_parens = colon_url.replace('#', '#(') + ')'
    a.assert_finds_whole_url(colon_url_with_parens)
    # This is a real testing domain, from:
    # http://en.wikipedia.org/wiki/List_of_TLDs#Test_TLDS
    a.assert_finds_whole_url('http://例子.測試')
    a.assert_no_url('http://br@n is the @wesome!!!')
    a.assert_no_url('ftp://user@example.com')
    # These are real reviews that were improperly linkified.
    a.assert_no_url(
        'My legs... my legs... must keep going...  must.......be' +
        '.....nearly.....there.....yet....HOLY SHIT IT CONTINUES?')
    a.assert_no_url('Great setting however....it was a bit loud.')
    a.assert_no_url(
        "I've been greatly disappointed with Gilmore's the last couple years" +
        "...it used to be my go-to spot in the burbs for French."
    )
    a.assert_no_url('isemail@emailaddress.com')

    a.assert_finds_url('http://www.foo.com/blah#foo', 'http://www.foo.com/blah#foo')
    a.assert_finds_url('http://www.foo.com/blah!', 'http://www.foo.com/blah')
    a.assert_finds_url('http://www.foo.com/blah_(disambiguation)', 'http://www.foo.com/blah_(disambiguation)')

    a.assert_finds_whole_url('http://Cervejoteca.com.br')


def test_url_regex():
    """Test that our url-matching regex and fast url/email matching regex work properly."""
    a = RegexAssertion(url_regex)
    assert_url_regex(a)

    # These are real examples of insurance spam on talk
    a.assert_finds_whole_url('LOANFINDERFAST.us')
    a.assert_finds_whole_url('LOANFINDERFAST.US')
    a.assert_finds_url('LOANFINDERFAST.us.', 'LOANFINDERFAST.us')
    a.assert_finds_url('LOANFINDERFAST.us-', 'LOANFINDERFAST.us')


def test_custom_regex():
    a = RegexAssertion(url_regex_common_tlds)
    assert_url_regex(a)

    a.assert_no_url('org.openqa.selenium.support.events') # events is a tld
    a.assert_no_url('EventFiringWebElement.click')        # click is a tld
    a.assert_no_url('os.name')                            # name is a tld
    a.assert_no_url('main.py')                            # py is a tld
    a.assert_no_url('foo.sh')                            # py is a tld
    a.assert_no_url('pid.id')                            # py is a tld

    a.assert_finds_url('Check out http://I.have.com?query!', 'http://I.have.com?query')
    a.assert_finds_whole_url('www.audrey_tsang.com')


def test_url_regex_i18n():
    a = RegexAssertion(url_regex)

    # We now know the list of non-ascii top-level domains as well:
    a.assert_finds_url(
        u'This is a website: 中国互联网络信息中心.中国. No, really.',
        u'中国互联网络信息中心.中国'
    )
    # We can't find internationalized TLDs in encoded strings, however.
    if not six.PY3:  # Regexes aren't valid for both bytes and str in py3
        a.assert_no_url(u'This is a website: 中国互联网络信息中心.中国. No, really.'.encode('UTF-8'))

    # But we should be able to find the punycoded TLDs in both cases:
    a.assert_finds_url(
        u'This is a website: 中国互联网络信息中心.xn--fiqs8s. No, really.',
        u'中国互联网络信息中心.xn--fiqs8s'
    )
    if not six.PY3:  # Regexes aren't valid for both bytes and str in py3
        a.assert_finds_url(
            u'This is a website: 中国互联网络信息中心.xn--fiqs8s. No, really.'.encode('UTF-8'),
            u'中国互联网络信息中心.xn--fiqs8s'.encode('UTF-8')
        )
