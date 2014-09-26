# -*- coding: utf-8 -*-
from yelp_uri.search import email_regex
from yelp_uri.search import url_regex


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


def test_url_regex():
    """Test that our url-matching regex and fast url/email matching regex work properly."""

    def assert_finds_url(text, url):
        match = url_regex.search(text)
        assert match is not None, "Expected url_regex match on " + url + " (text: '" + text + "')"
        assert match.group() == url

    def assert_finds_whole_url(url):
        assert_finds_url(url, url)

    def assert_no_url(text):
        assert url_regex.match(text) is None

    assert_finds_url('dictionary.com\'s', 'dictionary.com')
    assert_finds_url('yelp.com.', 'yelp.com')
    assert_finds_url('http://sensorydeprivation.co.uk is the person to talk to', 'http://sensorydeprivation.co.uk')
    assert_finds_url('Read https://www.girlgeniusonline.com', 'https://www.girlgeniusonline.com')
    assert_finds_url('look at this site with com in it: http://news.ycombinator.com', 'http://news.ycombinator.com')
    assert_finds_url('My site is http://example.com.I am bad at spacebar.', 'http://example.com')
    assert_finds_url('Check out http://I.have.com?query!', 'http://I.have.com?query')
    assert_finds_url('Check out http://I.have.com#!she/bang!', 'http://I.have.com#!she/bang')
    assert_finds_url('Follow @YelpCincy on Twitter (http://twitter.com/YelpCincy)', 'http://twitter.com/YelpCincy')
    assert_finds_url(
        'Reference: http://en.wikipedia.org/wiki/Eon_(geology)',
        'http://en.wikipedia.org/wiki/Eon_(geology)',
    )
    assert_finds_url('http://example.com:8O80', 'http://example.com')
    assert_finds_whole_url('http://example.com:8080')
    assert_finds_whole_url('http://lil_jay78.blogspot.com/')
    assert_finds_whole_url('http://yelp.com/berkeley')
    assert_finds_whole_url('www.audrey_tsang.com')
    assert_finds_whole_url('http://a.com')
    assert_finds_whole_url('http://who_even_uses_dot_mobi.mobi')
    assert_finds_whole_url(u'http://www.yelp.com/münchen')
    assert_finds_whole_url(u'http://www.ü.com/ü;ü;ü/ü;ü;ü?ü=ü&ü=ü#!ü/ü')
    assert_finds_whole_url(u'http://➡.ws/➡;➡;➡/➡;➡;➡?➡=➡&➡=➡#!➡/➡')
    assert_finds_whole_url('http://y.combinator')
    assert_finds_whole_url('http://.ocregion.com')
    # Ticket: #31242
    colon_url = 'http://www.yelp.fr/biz/smalls-marseille#hrid:u_UQvMf97E8pD4HEb59uIw'
    assert_finds_whole_url(colon_url)
    assert_finds_url('(%s)' % colon_url, colon_url)
    colon_url_with_parens = colon_url.replace('#', '#(') + ')'
    assert_finds_whole_url(colon_url_with_parens)
    # This is a real testing domain, from:
    # http://en.wikipedia.org/wiki/List_of_TLDs#Test_TLDS
    assert_finds_whole_url('http://例子.測試')
    assert_no_url('http://br@n is the @wesome!!!')
    assert_no_url('ftp://user@example.com')
    # These are real reviews that were improperly linkified.
    assert_no_url(
        'My legs... my legs... must keep going...  must.......be' +
        '.....nearly.....there.....yet....HOLY SHIT IT CONTINUES?')
    assert_no_url('Great setting however....it was a bit loud.')
    assert_no_url(
        "I've been greatly disappointed with Gilmore's the last couple years" +
        "...it used to be my go-to spot in the burbs for French."
    )

    assert_finds_url('http://www.foo.com/blah#foo', 'http://www.foo.com/blah#foo')
    assert_finds_url('http://www.foo.com/blah!', 'http://www.foo.com/blah')
    assert_finds_url('http://www.foo.com/blah_(disambiguation)', 'http://www.foo.com/blah_(disambiguation)')

    # These are real examples of insurance spam on talk
    assert_finds_whole_url('LOANFINDERFAST.us')
    assert_finds_whole_url('LOANFINDERFAST.US')
    assert_finds_url('LOANFINDERFAST.us.', 'LOANFINDERFAST.us')
    assert_finds_url('LOANFINDERFAST.us-', 'LOANFINDERFAST.us')

    assert_finds_whole_url('http://Cervejoteca.com.br')

    # We now know the list of non-ascii top-level domains as well:
    assert_finds_url(
        u'This is a website: 中国互联网络信息中心.中国. No, really.',
        u'中国互联网络信息中心.中国'
    )
    # We can't find internationalized TLDs in encoded strings, however.
    assert_no_url(b'This is a website: 中国互联网络信息中心.中国. No, really.')

    # But we should be able to find the punycoded TLDs in both cases:
    assert_finds_url(
        u'This is a website: 中国互联网络信息中心.xn--fiqs8s. No, really.',
        u'中国互联网络信息中心.xn--fiqs8s'
    )
    assert_finds_url(
        b'This is a website: 中国互联网络信息中心.xn--fiqs8s. No, really.',
        b'中国互联网络信息中心.xn--fiqs8s'
    )
