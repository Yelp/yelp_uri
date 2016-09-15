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
    def __init__(self, regex):
        self.url_regex = regex

    def finds_url(self, text, url):
        match = self.url_regex.search(text)
        assert match is not None, "Expected url_regex match on " + url + " (text: '" + text + "')"
        assert match.group() == url

    def finds_whole_url(self, url):
        self.finds_url(url, url)

    def finds_no_url(self, text):
        assert self.url_regex.match(text) is None


def assert_url_regex(regex_assert):

    regex_assert.finds_url('dictionary.com\'s', 'dictionary.com')
    regex_assert.finds_url('yelp.com.', 'yelp.com')
    regex_assert.finds_url('http://sensorydeprivation.co.uk is the person to talk to', 'http://sensorydeprivation.co.uk')
    regex_assert.finds_url('Read https://www.girlgeniusonline.com', 'https://www.girlgeniusonline.com')
    regex_assert.finds_url('look at this site with com in it: http://news.ycombinator.com', 'http://news.ycombinator.com')
    regex_assert.finds_url('My site is http://example.com.I am bad at spacebar.', 'http://example.com')
    regex_assert.finds_url('Check out http://I.have.com?query!', 'http://I.have.com?query')
    regex_assert.finds_url('Check out http://I.have.com#!she/bang!', 'http://I.have.com#!she/bang')
    regex_assert.finds_url('Follow @YelpCincy on Twitter (http://twitter.com/YelpCincy)', 'http://twitter.com/YelpCincy')
    regex_assert.finds_url(
        'Reference: http://en.wikipedia.org/wiki/Eon_(geology)',
        'http://en.wikipedia.org/wiki/Eon_(geology)',
    )
    regex_assert.finds_url('http://example.com:8O80', 'http://example.com')
    regex_assert.finds_url('notemail@https://example.com', 'https://example.com')
    regex_assert.finds_url('notemail@www.example.com', 'www.example.com')

    regex_assert.finds_whole_url('http://example.com:8080')
    regex_assert.finds_whole_url('http://lil_jay78.blogspot.com/')
    regex_assert.finds_whole_url('http://yelp.com/berkeley')
    regex_assert.finds_whole_url('www.audrey_tsang.com')
    regex_assert.finds_whole_url('http://a.com')
    regex_assert.finds_whole_url('http://who_even_uses_dot_mobi.mobi')
    regex_assert.finds_whole_url(u'http://www.yelp.com/münchen')
    regex_assert.finds_whole_url(u'http://www.ü.com/ü;ü;ü/ü;ü;ü?ü=ü&ü=ü#!ü/ü')
    regex_assert.finds_whole_url(u'http://➡.ws/➡;➡;➡/➡;➡;➡?➡=➡&➡=➡#!➡/➡')
    regex_assert.finds_whole_url('http://y.combinator')
    regex_assert.finds_whole_url('http://.ocregion.com')

    # Chops off everything after last tld, www.dmv.ca
    regex_assert.finds_url('https://www.dmv.ca.gov\\notpartofurl', 'https://www.dmv.ca.gov')
    # Chops off path after www.dmv.ca
    regex_assert.finds_url(
        'Contact the dmv: https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus\\nnext_paragraph',
        'https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus'
    )
    # Chops off path at the last period, which is the last bad_end
    regex_assert.finds_url(
        'Contact the dmv: https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus.html\\nnext_paragraph',
        'https://www.dmv.ca.gov/portal/dmv/dmvfooter2/contactus.html'
    )
    # :39 is a line number in this context but is valid path component
    regex_assert.finds_whole_url('https://media4.com/en_US.min.js:39')
    # Proves :39 is indeed the path component and not the port
    regex_assert.finds_whole_url('https://media4.com:443/en_US.min.js:39')

    # Ticket: #31242
    colon_url = 'http://www.yelp.fr/biz/smalls-marseille#hrid:u_UQvMf97E8pD4HEb59uIw'
    regex_assert.finds_whole_url(colon_url)
    regex_assert.finds_url('(%s)' % colon_url, colon_url)
    colon_url_with_parens = colon_url.replace('#', '#(') + ')'
    regex_assert.finds_whole_url(colon_url_with_parens)
    # This is a real testing domain, from:
    # http://en.wikipedia.org/wiki/List_of_TLDs#Test_TLDS
    regex_assert.finds_whole_url('http://例子.測試')
    regex_assert.finds_no_url('http://br@n is the @wesome!!!')
    regex_assert.finds_no_url('ftp://user@example.com')
    # These are real reviews that were improperly linkified.
    regex_assert.finds_no_url(
        'My legs... my legs... must keep going...  must.......be' +
        '.....nearly.....there.....yet....HOLY SHIT IT CONTINUES?')
    regex_assert.finds_no_url('Great setting however....it was a bit loud.')
    regex_assert.finds_no_url(
        "I've been greatly disappointed with Gilmore's the last couple years" +
        "...it used to be my go-to spot in the burbs for French."
    )
    regex_assert.finds_no_url('isemail@emailaddress.com')

    regex_assert.finds_url('http://www.foo.com/blah#foo', 'http://www.foo.com/blah#foo')
    regex_assert.finds_url('http://www.foo.com/blah!', 'http://www.foo.com/blah')
    regex_assert.finds_url('http://www.foo.com/blah_(disambiguation)', 'http://www.foo.com/blah_(disambiguation)')

    regex_assert.finds_whole_url('http://Cervejoteca.com.br')


def test_url_regex():
    """Test that our url-matching regex and fast url/email matching regex work properly."""
    a = RegexAssertion(url_regex)
    assert_url_regex(a)

    # These are real examples of insurance spam on talk
    a.finds_whole_url('LOANFINDERFAST.us')
    a.finds_whole_url('LOANFINDERFAST.US')
    a.finds_url('LOANFINDERFAST.us.', 'LOANFINDERFAST.us')
    a.finds_url('LOANFINDERFAST.us-', 'LOANFINDERFAST.us')


def test_custom_regex():
    a = RegexAssertion(url_regex_common_tlds)
    assert_url_regex(a)

    # Uncommon tld that are common text patterns in code and configs
    a.finds_no_url('org.openqa.selenium.support.events')
    a.finds_no_url('EventFiringWebElement.click')
    a.finds_no_url('os.name')
    a.finds_no_url('main.py')
    a.finds_no_url('foo.sh')
    a.finds_no_url('pid.id')

    a.finds_url('Check out http://I.have.com?query!', 'http://I.have.com?query')
    a.finds_whole_url('www.audrey_tsang.com')


def test_url_regex_i18n():
    a = RegexAssertion(url_regex)

    # We now know the list of non-ascii top-level domains as well:
    a.finds_url(
        u'This is a website: 中国互联网络信息中心.中国. No, really.',
        u'中国互联网络信息中心.中国'
    )
    # We can't find internationalized TLDs in encoded strings, however.
    if not six.PY3:  # Regexes aren't valid for both bytes and str in py3
        a.finds_no_url(u'This is a website: 中国互联网络信息中心.中国. No, really.'.encode('UTF-8'))

    # But we should be able to find the punycoded TLDs in both cases:
    a.finds_url(
        u'This is a website: 中国互联网络信息中心.xn--fiqs8s. No, really.',
        u'中国互联网络信息中心.xn--fiqs8s'
    )
    if not six.PY3:  # Regexes aren't valid for both bytes and str in py3
        a.finds_url(
            u'This is a website: 中国互联网络信息中心.xn--fiqs8s. No, really.'.encode('UTF-8'),
            u'中国互联网络信息中心.xn--fiqs8s'.encode('UTF-8')
        )
