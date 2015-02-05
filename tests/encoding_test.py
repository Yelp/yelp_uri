# -*- coding: utf-8 -*-
# pylint:disable=protected-access
import pytest
import yelp_uri.encoding as E
from yelp_uri.urllib_utf8 import quote


def test_uri_error():
    # Exception handlers around recode catch UnicodeError
    assert issubclass(E.MalformedUrlError, UnicodeError), type.mro(E.MalformedUrlError)


def test_bad_port():
    try:
        E.encode_uri('http://foo.bar:buz')
    except E.MalformedUrlError as error:
        assert error.args == ("Invalid port number: invalid literal for int() with base 10: 'buz'",)


def test_bad_domain_segment_too_long():
    try:
        E.encode_uri('http://foo.%s.bar' % ('x' * 64))
    except E.MalformedUrlError as error:
        assert error.args == (
            "Invalid hostname: label empty or too long: " +
            "'foo.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.bar'",
        )


def test_bad_domain_extra_dots():
    # We normalize this one ala Chrome browser
    assert E.encode_uri('http://..foo..com../.bar.') == 'http://foo.com/.bar.'


def test_unicode_url_gets_quoted():
    url = u'http://www.yelp.com/münchen'
    assert E.recode_uri(url) == 'http://www.yelp.com/m%C3%BCnchen'


def test_mixed_quoting_url():
    """Test that a url with mixed quoting has uniform quoting after requoting"""
    url = u'http://www.yelp.com/m%C3%BCnchen/münchen'
    assert E.recode_uri(url) == 'http://www.yelp.com/m%C3%BCnchen/m%C3%BCnchen'


def test_mixed_quoting_param():
    """Tests that a url with mixed quoting in the parameters has uniform quoting after requoting"""
    url = u'http://www.yelp.com?m%C3%BCnchen=münchen'
    assert E.recode_uri(url) == 'http://www.yelp.com?m%C3%BCnchen=m%C3%BCnchen'


def test_mixed_encoding():
    """Tests that a url with mixed encoding has uniform encoding after recoding"""
    url = u'http://www.yelp.com/m%C3%BCnchen?m%FCnchen'
    assert E.recode_uri(url) == 'http://www.yelp.com/m%C3%BCnchen?m%C3%BCnchen'


def test_mixed_quoting_multiple_queries():
    """Tests that a url with mixed quoting in multiple parameters has uniform quoting after requoting"""
    url = u'http://yelp.com/münchen/m%C3%BCnchen?münchen=m%C3%BCnchen&htmlchars=<">'
    assert E.recode_uri(url) == \
        'http://yelp.com/m%C3%BCnchen/m%C3%BCnchen?m%C3%BCnchen=m%C3%BCnchen&htmlchars=%3C%22%3E'


def test_utf8_url():
    """Tests that a url with mixed quoting in multiple parameters has uniform quoting after requoting"""
    url = u'http://yelp.com/münchen/m%C3%BCnchen?münchen=m%C3%BCnchen&htmlchars=<">'.encode('utf-8')
    assert E.recode_uri(url) == \
        'http://yelp.com/m%C3%BCnchen/m%C3%BCnchen?m%C3%BCnchen=m%C3%BCnchen&htmlchars=%3C%22%3E'


def test_multiple_escapes():
    url = u'http://münch.com?zero=münch&one=m%C3%BCnch&two=m%25C3%25BCnch&three=m%2525C3%2525BCnch'
    assert E.recode_uri(url) == \
        'http://xn--mnch-0ra.com?zero=m%C3%BCnch&one=m%C3%BCnch&two=m%25C3%25BCnch&three=m%2525C3%2525BCnch'


def test_url_reserved_chars():
    url = 'http://www.yelp.com?chars=%s' % quote(':/?&=')
    assert E.recode_uri(url) == url


def test_multi_params_for_individual_path_segment():
    # Nothing (overly) strange in this url: nothing should be escaped
    url = '/foo;bar;baz/barney;fred;wilma'
    assert E.recode_uri(url) == url


def test_url_with_params():
    url = (
        'http://ad.doubleclick.net/clk;217976351;41128009;f?'
        'http%3A//www.24hourfitness.com/FindClubDetail.do?'
        'clubid=189&edit=null&semiPromoCode=null&cm_mmc='
        'Yelp-_-ClubPage-_-BusinessListing-_-Link'
    )
    assert E.recode_uri(url) == url


def test_url_with_hashbang():
    # For a discussion of url hashbangs, see: http://www.jenitennison.com/blog/node/154
    url = 'https://twitter.com/#!/YelpCincy/statuses/179565284020060161'
    assert E.recode_uri(url) == url


def test_url_with_colon():
    # Ticket: 31242
    url = 'http://www.yelp.fr/biz/smalls-marseille#hrid:u_UQvMf97E8pD4HEb59uIw'
    assert E.recode_uri(url) == url


def test_param_xss():
    assert E.recode_uri('/foo;<script>;baz/barney;%2F%3B%25;wilma') == '/foo;%3Cscript%3E;baz/barney;%2F%3B%25;wilma'


def test_letters_recoding():
    """Tests that alphanumeric escapes get unquoted in recode_uri."""
    url = u'http://💩.la/%74%68%69%73%5f%69%73%5f%61%5f%70%61%74%68?a=b%3f%63&%64%3D%65=f#%73%70%61%63%65%73 %61%72%65 %64%61%6e%67%65%72%6f%75%73'
    assert E.recode_uri(url) == \
        'http://xn--ls8h.la/this_is_a_path?a=b%3fc&d%3De=f#spaces%20are%20dangerous'


def worst_case(strange_character):
    u"""
    generate a worst-case url, using a "strange" character

    >>> print worst_case(u'ü')
    http://ü:ü@www.ü.com/ü;ü;ü/ü;ü;ü?ü=ü&ü=ü#!ü/ü
    """
    return strange_character.join(
        ('http://', ':', '@www.', '.com/', ';', ';', '/', ';', ';', '?', '=', '&', '=', '#!', '/', ''))


def test_worst_case_unicode():
    # Test both unicode and utf8-bytes
    for umlaut in (u'ü', 'ü'):
        strange_url = worst_case(umlaut)
        normalized_url = E.recode_uri(strange_url)

        # I think this makes things more readable
        processed = normalized_url.replace('%C3%BC', '%')
        assert processed == 'http://%:%@www.xn--tda.com/%;%;%/%;%;%?%=%&%=%#!%/%'


def test_worst_case_ascii():
    for ascii_char in '<> ':
        strange_url = worst_case(ascii_char)
        normalized_url = E.recode_uri(strange_url)

        escaped_char = '%%%2X' % ord(ascii_char)
        assert escaped_char in normalized_url

        # I think this makes things more readable
        processed = normalized_url.replace(ascii_char, '{ascii_char}')
        processed = processed.replace(escaped_char, '%')
        assert processed == 'http://%:%@www.{ascii_char}.com/%;%;%/%;%;%?%=%&%=%#!%/%'


def test_bad_bytes():
    # This is unlikely to happen except due to gross programming error,
    # but I want to show what *would* happen.
    for bad_stuff in (u'\xFF', '\xFF', '%FF'):
        strange_url = worst_case(bad_stuff)
        normalized_url = E.recode_uri(strange_url)

        # I think this makes things more readable
        processed = normalized_url.replace('%C3%BF', '%')
        assert processed == 'http://%:%@www.xn--wda.com/%;%;%/%;%;%?%=%&%=%#!%/%'


def test_dots_fixup():
    # Real-world example:
    # http://www.yelp.com/biz/orange-county-church-of-christ-irvine
    strange_url = 'http://.ocregion.com'
    normalized_url = E.recode_uri(strange_url)
    assert normalized_url == 'http://ocregion.com'

    # Extreme example
    strange_url = 'http://guest@....example....com....:8080/'
    normalized_url = E.recode_uri(strange_url)
    assert normalized_url == 'http://guest@example.com:8080/'


def test_bad_domain():
    # domain names with segments over length 64 are un-encodable by the idna codec
    strange_url = 'http://www.%s.com/' % ('x' * 64)
    with pytest.raises(UnicodeError):
        E.recode_uri(strange_url)


def test_bad_port2():
    # Similarly, we raise UnicodeError for
    strange_url = 'http://www.example.com:80wtf80/'
    with pytest.raises(UnicodeError):
        E.recode_uri(strange_url)


def test_bad_user():
    # This was previously throwing UnicodeError via idna codec, but I've
    # fixed it.
    strange_url = 'http://user....@www.example.com/'
    assert E.recode_uri(strange_url) == strange_url


def test_yelp_scheme_url():
    strange_url = 'yelp:///example'
    assert E.recode_uri(strange_url) == strange_url


def test_relative_url():
    strange_url = '➨.ws/➨'
    expected = '%E2%9E%A8.ws/%E2%9E%A8'
    processed = E.recode_uri(strange_url)
    assert processed == expected


def test_path_only_url():
    strange_url = '/➨ ?➨ #➨ '
    expected = '/%E2%9E%A8%20?%E2%9E%A8%20#%E2%9E%A8%20'
    processed = E.recode_uri(strange_url)
    assert processed == expected


examples = pytest.mark.parametrize(('charname', 'chars', 'pathchars', 'expected_url'), [
    ('latin1', u'ü', u'\x81', 'http://xn--mnchen-3ya.com/m%C3%BCchen/%C2%81'),
    ('win1252', u'€', '', 'http://xn--mnchen-ic1c.com/m%E2%82%ACchen/'),
    ('utf8', u'プŁ☃', '', 'http://xn--mnchen-3db6836e0mua.com/m%E3%83%97%C5%81%E2%98%83chen/'),
    ('emoji', u'🐱', '', 'http://xn--mnchen-i844e.com/m%F0%9F%90%B1chen/'),
    ('ascii', '-._~%', "!$&'()*+,;=:@", "http://m-._~%nchen.com/m-._~%chen/!$&'()*+,;=:@")
])


@examples
def test_recode_unicode(charname, chars, pathchars, expected_url):
    del charname  # passed, but unused
    url_template = "http://m{chars}nchen.com/m{chars}chen/{pathchars}"
    unicode_url = url_template.decode('ascii').format(chars=chars, pathchars=pathchars)
    assert E.recode_uri(unicode_url) == expected_url


@examples
@pytest.mark.parametrize('encoding', ('latin1', 'windows-1252', 'utf8', 'ascii'))
def test_recode_encoded(charname, chars, pathchars, expected_url, encoding):
    url_template = "http://m{chars}nchen.com/m{chars}chen/{pathchars}"
    unicode_url = url_template.decode('ascii').format(chars=chars, pathchars=pathchars)

    try:
        encoded_url = unicode_url.encode(encoding)
    except UnicodeEncodeError:
        pytest.skip("Some of these things just won't go.")

    assert E.recode_uri(encoded_url) == expected_url

    quoted_url = url_template.format(
        chars=quote(chars.encode(encoding)),
        pathchars=quote(pathchars.encode(encoding)),
    )
    if charname == 'ascii':
        # ASCII is a special case when it comes to quoting: their quoted-ness should go untouched.
        assert E.recode_uri(quoted_url) == quoted_url
    else:
        assert E.recode_uri(quoted_url) == expected_url


class TestUnquoteBytes(object):
    ASCII = ''.join(chr(c) for c in range(0x80))
    NON_ASCII = ''.join(chr(c) for c in range(0x80, 0x100))

    @staticmethod
    def assert_unquote_bytes(input_value, expected):
        assert E._unquote_bytes(input_value) == expected

    def test_dont_touch_unquoted_ascii(self):
        url = 'http://yelp.com/' + self.ASCII
        self.assert_unquote_bytes(url, url)

    def test_dont_touch_quoted_ascii(self):
        quoted_ascii = quote(self.ASCII)
        url = 'http://yelp.com/' + quoted_ascii
        self.assert_unquote_bytes(url, url)

    def test_dont_touch_unquoted_nonascii(self):
        unquoted_url = 'http://yelp.com/' + self.NON_ASCII
        self.assert_unquote_bytes(unquoted_url, unquoted_url)

    def test_unescape_quoted_nonascii(self):
        quoted_non_ascii = quote(self.NON_ASCII)
        unquoted_url = 'http://yelp.com/' + self.NON_ASCII
        quoted_url = 'http://yelp.com/' + quoted_non_ascii
        self.assert_unquote_bytes(quoted_url, unquoted_url)


class TestRecodeEmail(object):
    munchen = u'münchen'
    email = u'{munchen}@{munchen}.com?subject={munchen}'.format(munchen=munchen)

    # The username is best encoded as simply utf8.
    expected = u'{utf8_munchen}@{idna_munchen}.com?subject={percent_munchen}'.format(
        utf8_munchen=munchen,
        idna_munchen=munchen.encode('IDNA'),
        percent_munchen=quote(munchen.encode('UTF-8')),
    )

    @staticmethod
    def test_empty_string():
        assert E.encode_email('') == ''

    def test_not_an_email(self):
        not_an_email = u"They don't use email in " + self.munchen
        assert E.encode_email(not_an_email) == not_an_email.encode('IDNA')

    def test_encode_email(self):
        assert E.encode_email(self.email) == self.expected

    def test_decode_email(self):
        assert E.decode_email(self.expected) == self.email

    def test_recode_email(self):
        assert E.recode_email(self.email) == self.expected

    # Tests for idempotency:
    def test_encode_email_idempotent(self):
        assert E.encode_email(E.encode_email(self.email)) == self.expected

    def test_decode_email_idempotent(self):
        assert E.decode_email(E.decode_email(self.expected)) == self.email

    def test_recode_email_idempotent(self):
        assert E.recode_email(E.recode_email(self.email)) == self.expected

    def test_mailto_scheme(self):
        assert E.recode_email('mailto:' + self.email) == 'mailto:' + self.expected

        # This is technically wrong, but we fix it.
        assert E.recode_email('mailto://' + self.email) == 'mailto:' + self.expected
