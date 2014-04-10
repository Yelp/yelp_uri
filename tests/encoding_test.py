# -*- coding: utf-8 -*-
import pytest
import yelp_uri.encoding as E
from yelp_uri.urllib_utf8 import quote


class TestBadURIs(object):
    def test_uri_error(self):
        # Exception handlers around recode catch UnicodeError
        assert issubclass(E.MalformedUrlError, UnicodeError), E.MalformedUrlError.mro()

    def test_bad_port(self):
        try:
            E.encode_uri('http://foo.bar:buz')
        except E.MalformedUrlError, e:
            assert e.args == ("Invalid port number: invalid literal for int() with base 10: 'buz'",)

    def test_bad_domain_segment_too_long(self):
        try:
            E.encode_uri('http://foo.%s.bar' % ('x' * 64))
        except E.MalformedUrlError, e:
            assert e.args == (
                "Invalid hostname: label empty or too long: " +
                "'foo.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.bar'",
            )

    def test_bad_domain_extra_dots(self):
        # We normalize this one ala Chrome browser
        assert E.encode_uri('http://..foo..com../.bar.') == 'http://foo.com/.bar.'


class TestRecode(object):
    def test_unicode_url_gets_quoted(self):
        url = u'http://www.yelp.com/münchen'
        assert E.recode_uri(url) == 'http://www.yelp.com/m%C3%BCnchen'

    def test_mixed_quoting_url(self):
        """Test that a url with mixed quoting has uniform quoting after requoting"""
        url = u'http://www.yelp.com/m%C3%BCnchen/münchen'
        assert E.recode_uri(url) == 'http://www.yelp.com/m%C3%BCnchen/m%C3%BCnchen'

    def test_mixed_quoting_param(self):
        """Tests that a url with mixed quoting in the parameters has uniform quoting after requoting"""
        url = u'http://www.yelp.com?m%C3%BCnchen=münchen'
        assert E.recode_uri(url) == 'http://www.yelp.com?m%C3%BCnchen=m%C3%BCnchen'

    def test_mixed_quoting_multiple_queries(self):
        """Tests that a url with mixed quoting in multiple parameters has uniform quoting after requoting"""
        url = u'http://yelp.com/münchen/m%C3%BCnchen?münchen=m%C3%BCnchen&htmlchars=<">'
        assert E.recode_uri(url) == \
            'http://yelp.com/m%C3%BCnchen/m%C3%BCnchen?m%C3%BCnchen=m%C3%BCnchen&htmlchars=%3C%22%3E'

    def test_utf8_url(self):
        """Tests that a url with mixed quoting in multiple parameters has uniform quoting after requoting"""
        url = u'http://yelp.com/münchen/m%C3%BCnchen?münchen=m%C3%BCnchen&htmlchars=<">'.encode('utf-8')
        assert E.recode_uri(url) == \
            'http://yelp.com/m%C3%BCnchen/m%C3%BCnchen?m%C3%BCnchen=m%C3%BCnchen&htmlchars=%3C%22%3E'

    def test_multiple_escapes(self):
        url = u'http://münch.com?zero=münch&one=m%C3%BCnch&two=m%25C3%25BCnch&three=m%2525C3%2525BCnch'
        assert E.recode_uri(url) == \
            'http://xn--mnch-0ra.com?zero=m%C3%BCnch&one=m%C3%BCnch&two=m%25C3%25BCnch&three=m%2525C3%2525BCnch'

    def test_url_reserved_chars(self):
        url = 'http://www.yelp.com?chars=%s' % quote(':/?&=')
        assert E.recode_uri(url) == url

    def test_multi_params_for_individual_path_segment(self):
        # Nothing (overly) strange in this url: nothing should be escaped
        url = '/foo;bar;baz/barney;fred;wilma'
        assert E.recode_uri(url) == url

    def test_url_with_params(self):
        url = (
            'http://ad.doubleclick.net/clk;217976351;41128009;f?'
            'http%3A//www.24hourfitness.com/FindClubDetail.do?'
            'clubid=189&edit=null&semiPromoCode=null&cm_mmc='
            'Yelp-_-ClubPage-_-BusinessListing-_-Link'
        )
        assert E.recode_uri(url) == url

    def test_url_with_hashbang(self):
        # For a discussion of url hashbangs, see: http://www.jenitennison.com/blog/node/154
        url = 'https://twitter.com/#!/YelpCincy/statuses/179565284020060161'
        assert E.recode_uri(url) == url

    def test_url_with_colon(self):
        # Ticket: 31242
        url = 'http://www.yelp.fr/biz/smalls-marseille#hrid:u_UQvMf97E8pD4HEb59uIw'
        assert E.recode_uri(url) == url

    def test_param_xss(self):
        assert E.recode_uri('/foo;<script>;baz/barney;%2F%3B%25;wilma') == '/foo;%3Cscript%3E;baz/barney;%2F%3B%25;wilma'

    def worst_case(self, strange_character):
        """
        generate a worst-case url, using a "strange" character

        >>> self.worst_case(u'ü')
        u'http://ü:ü@www.ü.com/ü;ü;ü/ü;ü;ü?ü=ü&ü=ü#!ü/ü'
        """
        return strange_character.join(
            ('http://', ':', '@www.', '.com/', ';', ';', '/', ';', ';', '?', '=', '&', '=', '#!', '/', ''))

    def test_worst_case_unicode(self):
        # Test both unicode and utf8-bytes
        for umlat in (u'ü', 'ü'):
            strange_url = self.worst_case(u'ü')
            normalized_url = E.recode_uri(strange_url)

            # I think this makes things more readable
            processed = normalized_url.replace('%C3%BC', '%')
            assert processed == 'http://%:%@www.xn--tda.com/%;%;%/%;%;%?%=%&%=%#!%/%'

    def test_worst_case_ascii(self):
        for ascii_char in '<> ':
            strange_url = self.worst_case(ascii_char)
            normalized_url = E.recode_uri(strange_url)

            escaped_char = '%%%2X' % ord(ascii_char)
            assert escaped_char in normalized_url

            # I think this makes things more readable
            processed = normalized_url.replace(ascii_char, '{ascii_char}')
            processed = processed.replace(escaped_char, '%')
            assert processed == 'http://%:%@www.{ascii_char}.com/%;%;%/%;%;%?%=%&%=%#!%/%'

    def test_bad_bytes(self):
        # This is unlikely to happen except due to gross programming error,
        # but I want to show what *would* happen.
        for bad_stuff in (u'\xFF', '\xFF', '%FF'):
            strange_url = self.worst_case(bad_stuff)
            normalized_url = E.recode_uri(strange_url)

            # I think this makes things more readable
            processed = normalized_url.replace('%C3%BF', '%')
            assert processed == 'http://%:%@www.xn--wda.com/%;%;%/%;%;%?%=%&%=%#!%/%'

    def test_dots_fixup(self):
        # Real-world example:
        # http://www.yelp.com/biz/orange-county-church-of-christ-irvine
        strange_url = 'http://.ocregion.com'
        normalized_url = E.recode_uri(strange_url)
        assert normalized_url == 'http://ocregion.com'

        # Extreme example
        strange_url = 'http://guest@....example....com....:8080/'
        normalized_url = E.recode_uri(strange_url)
        assert normalized_url == 'http://guest@example.com:8080/'

    def test_bad_domain(self):
        # domain names with segments over length 64 are un-encodable by the idna codec
        strange_url = 'http://www.%s.com/' % ('x' * 64)
        with pytest.raises(UnicodeError):
            E.recode_uri(strange_url)

    def test_bad_port(self):
        # Similarly, we raise UnicodeError for
        strange_url = 'http://www.example.com:80wtf80/'
        with pytest.raises(UnicodeError):
            E.recode_uri(strange_url)

    def test_bad_user(self):
        # This was previously throwing UnicodeError via idna codec, but I've
        # fixed it.
        strange_url = 'http://user....@www.example.com/'
        assert E.recode_uri(strange_url) == strange_url

    def test_yelp_scheme_url(self):
        strange_url = 'yelp:///example'
        assert E.recode_uri(strange_url) == strange_url

    def test_relative_url(self):
        strange_url = '➨.ws/➨'
        expected = '%E2%9E%A8.ws/%E2%9E%A8'
        processed = E.recode_uri(strange_url)
        assert processed == expected

    def test_path_only_url(self):
        strange_url = '/➨ ?➨ #➨ '
        expected = '/%E2%9E%A8%20?%E2%9E%A8%20#%E2%9E%A8%20'
        processed = E.recode_uri(strange_url)
        assert processed == expected


@pytest.mark.parametrize(('charname', 'chars', 'pathchars', 'expected_url'), [
    ('latin1', u'ü', u'\x81', 'http://xn--mnchen-3ya.com/m%C3%BCchen/%C2%81'),
    ('win1252', u'€', '', 'http://xn--mnchen-ic1c.com/m%E2%82%ACchen/'),
    ('utf8', u'プŁ☃', '', 'http://xn--mnchen-3db6836e0mua.com/m%E3%83%97%C5%81%E2%98%83chen/'),
    ('emoji', u'🐱', '', 'http://xn--mnchen-i844e.com/m%F0%9F%90%B1chen/'),
    ('ascii', '-._~%', "!$&'()*+,;=:@", "http://m-._~%nchen.com/m-._~%chen/!$&'()*+,;=:@")
])
def test_recode_encoding(charname, chars, pathchars, expected_url):
    url_template = "http://m{chars}nchen.com/m{chars}chen/{pathchars}"
    unicode_url = url_template.decode('ascii').format(chars=chars, pathchars=pathchars)

    assert E.recode_uri(unicode_url) == expected_url

    for encoding in ('latin1', 'windows-1252', 'utf8', 'ascii'):
        try:
            encoded_url = unicode_url.encode(encoding)
        except UnicodeEncodeError:
            # Some of these things just won't go.
            continue

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

    def assert_unquote_bytes(self, input_value, expected):
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

    def test_empty_string(self):
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
