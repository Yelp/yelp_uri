# -*- coding: utf-8 -*-
import re

from yelp_uri import RFC3986

# Disable line number limit for the domains regex:
# pylint: disable=C0301

# Generated from generate_domains.py script.
domains = r"AC|ACADEMY|ACCOUNTANTS|ACTIVE|ACTOR|AD|AE|AERO|AF|AG|AGENCY|AI|AIRFORCE|AL|AM|AN|AO|AQ|AR|ARCHI|ARMY|ARPA|AS|ASIA|ASSOCIATES|AT|ATTORNEY|AU|AUCTION|AUDIO|AUTOS|AW|AX|AXA|AZ|BA|BAR|BARGAINS|BAYERN|BB|BD|BE|BEER|BERLIN|BEST|BF|BG|BH|BI|BID|BIKE|BIO|BIZ|BJ|BLACK|BLACKFRIDAY|BLUE|BM|BMW|BN|BNPPARIBAS|BO|BOO|BOUTIQUE|BR|BRUSSELS|BS|BT|BUILD|BUILDERS|BUSINESS|BUZZ|BV|BW|BY|BZ|BZH|CA|CAB|CAMERA|CAMP|CANCERRESEARCH|CAPETOWN|CAPITAL|CARAVAN|CARDS|CARE|CAREER|CAREERS|CASH|CAT|CATERING|CC|CD|CENTER|CEO|CERN|CF|CG|CH|CHEAP|CHRISTMAS|CHURCH|CI|CITIC|CITY|CK|CL|CLAIMS|CLEANING|CLICK|CLINIC|CLOTHING|CLUB|CM|CN|CO|CODES|COFFEE|COLLEGE|COLOGNE|COM|COMMUNITY|COMPANY|COMPUTER|CONDOS|CONSTRUCTION|CONSULTING|CONTRACTORS|COOKING|COOL|COOP|COUNTRY|CR|CREDIT|CREDITCARD|CRUISES|CU|CUISINELLA|CV|CW|CX|CY|CYMRU|CZ|DAD|DANCE|DATING|DAY|DE|DEALS|DEGREE|DEMOCRAT|DENTAL|DENTIST|DESI|DIAMONDS|DIET|DIGITAL|DIRECT|DIRECTORY|DISCOUNT|DJ|DK|DM|DNP|DO|DOMAINS|DURBAN|DZ|EAT|EC|EDU|EDUCATION|EE|EG|EMAIL|ENGINEER|ENGINEERING|ENTERPRISES|EQUIPMENT|ER|ES|ESQ|ESTATE|ET|EU|EUS|EVENTS|EXCHANGE|EXPERT|EXPOSED|FAIL|FARM|FEEDBACK|FI|FINANCE|FINANCIAL|FISH|FISHING|FITNESS|FJ|FK|FLIGHTS|FLORIST|FM|FO|FOO|FOUNDATION|FR|FRL|FROGANS|FUND|FURNITURE|FUTBOL|GA|GAL|GALLERY|GB|GBIZ|GD|GE|GENT|GF|GG|GH|GI|GIFT|GIFTS|GIVES|GL|GLASS|GLOBAL|GLOBO|GM|GMAIL|GMO|GMX|GN|GOP|GOV|GP|GQ|GR|GRAPHICS|GRATIS|GREEN|GRIPE|GS|GT|GU|GUIDE|GUITARS|GURU|GW|GY|HAMBURG|HAUS|HEALTHCARE|HELP|HERE|HIPHOP|HIV|HK|HM|HN|HOLDINGS|HOLIDAY|HOMES|HORSE|HOST|HOSTING|HOUSE|HOW|HR|HT|HU|ID|IE|IL|IM|IMMO|IMMOBILIEN|IN|INDUSTRIES|INFO|ING|INK|INSTITUTE|INSURE|INT|INTERNATIONAL|INVESTMENTS|IO|IQ|IR|IS|IT|JE|JETZT|JM|JO|JOBS|JOBURG|JP|JUEGOS|KAUFEN|KE|KG|KH|KI|KIM|KITCHEN|KIWI|KM|KN|KOELN|KP|KR|KRD|KRED|KW|KY|KZ|LA|LACAIXA|LAND|LAWYER|LB|LC|LEASE|LGBT|LI|LIFE|LIGHTING|LIMITED|LIMO|LINK|LK|LOANS|LONDON|LOTTO|LR|LS|LT|LTDA|LU|LUXE|LUXURY|LV|LY|MA|MAISON|MANAGEMENT|MANGO|MARKET|MARKETING|MC|MD|ME|MEDIA|MEET|MELBOURNE|MEME|MENU|MG|MH|MIAMI|MIL|MINI|MK|ML|MM|MN|MO|MOBI|MODA|MOE|MONASH|MORTGAGE|MOSCOW|MOTORCYCLES|MOV|MP|MQ|MR|MS|MT|MU|MUSEUM|MV|MW|MX|MY|MZ|NA|NAGOYA|NAME|NAVY|NC|NE|NET|NETWORK|NEUSTAR|NEW|NF|NG|NGO|NHK|NI|NINJA|NL|NO|NP|NR|NRA|NRW|NU|NYC|NZ|OKINAWA|OM|ONG|ONL|OOO|ORG|ORGANIC|OTSUKA|OVH|PA|PARIS|PARTNERS|PARTS|PE|PF|PG|PH|PHARMACY|PHOTO|PHOTOGRAPHY|PHOTOS|PHYSIO|PICS|PICTURES|PINK|PIZZA|PK|PL|PLACE|PLUMBING|PM|PN|POST|PR|PRAXI|PRESS|PRO|PROD|PRODUCTIONS|PROPERTIES|PROPERTY|PS|PT|PUB|PW|PY|QA|QPON|QUEBEC|RE|REALTOR|RECIPES|RED|REHAB|REISE|REISEN|REN|RENTALS|REPAIR|REPORT|REPUBLICAN|REST|RESTAURANT|REVIEWS|RICH|RIO|RO|ROCKS|RODEO|RS|RSVP|RU|RUHR|RW|RYUKYU|SA|SAARLAND|SARL|SB|SC|SCA|SCB|SCHMIDT|SCHULE|SCOT|SD|SE|SERVICES|SEXY|SG|SH|SHIKSHA|SHOES|SI|SINGLES|SJ|SK|SL|SM|SN|SO|SOCIAL|SOFTWARE|SOHU|SOLAR|SOLUTIONS|SOY|SPACE|SPIEGEL|SR|ST|SU|SUPPLIES|SUPPLY|SUPPORT|SURF|SURGERY|SUZUKI|SV|SX|SY|SYSTEMS|SZ|TATAR|TATTOO|TAX|TC|TD|TECHNOLOGY|TEL|TF|TG|TH|TIENDA|TIPS|TIROL|TJ|TK|TL|TM|TN|TO|TODAY|TOKYO|TOOLS|TOP|TOWN|TOYS|TP|TR|TRADE|TRAINING|TRAVEL|TT|TV|TW|TZ|UA|UG|UK|UNIVERSITY|UNO|UOL|US|UY|UZ|VA|VACATIONS|VC|VE|VEGAS|VENTURES|VERSICHERUNG|VET|VG|VI|VIAJES|VILLAS|VISION|VLAANDEREN|VN|VODKA|VOTE|VOTING|VOTO|VOYAGE|VU|WALES|WANG|WATCH|WEBCAM|WEBSITE|WED|WF|WHOSWHO|WIEN|WIKI|WILLIAMHILL|WME|WORKS|WS|WTC|WTF|XN--1QQW23A|XN--3BST00M|XN--3DS443G|XN--3E0B707E|XN--45BRJ9C|XN--4GBRIM|XN--55QW42G|XN--55QX5D|XN--6FRZ82G|XN--6QQ986B3XL|XN--80ADXHKS|XN--80AO21A|XN--80ASEHDB|XN--80ASWG|XN--90A3AC|XN--C1AVG|XN--CG4BKI|XN--CLCHC0EA0B2G2A9GCD|XN--CZR694B|XN--CZRU2D|XN--D1ACJ3B|XN--FIQ228C5HS|XN--FIQ64B|XN--FIQS8S|XN--FIQZ9S|XN--FPCRJ9C3D|XN--FZC2C9E2C|XN--GECRJ9C|XN--H2BRJ9C|XN--I1B6B1A6A2E|XN--IO0A7I|XN--J1AMH|XN--J6W193G|XN--KPRW13D|XN--KPRY57D|XN--KPUT3I|XN--L1ACC|XN--LGBBAT1AD8J|XN--MGB9AWBF|XN--MGBA3A4F16A|XN--MGBAAM7A8H|XN--MGBAB2BD|XN--MGBAYH7GPA|XN--MGBBH1A71E|XN--MGBC0A9AZCG|XN--MGBERP4A5D4AR|XN--MGBX4CD0AB|XN--NGBC5AZD|XN--NQV7F|XN--NQV7FS00EMA|XN--O3CW4H|XN--OGBPF8FL|XN--P1AI|XN--PGBS0DH|XN--Q9JYB4C|XN--RHQV96G|XN--S9BRJ9C|XN--SES554G|XN--UNUP4Y|XN--VHQUV|XN--WGBH1C|XN--WGBL6A|XN--XHQ521B|XN--XKC2AL3HYE2A|XN--XKC2DL3A5EE0H|XN--YFRO4I67O|XN--YGBI2AMMX|XN--ZFR164B|XXX|XYZ|YACHTS|YANDEX|YE|YOKOHAMA|YOUTUBE|YT|ZA|ZM|ZONE|ZW"

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
            (%(domains)s)
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
        domains=domains,
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
