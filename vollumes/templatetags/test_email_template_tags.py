from django.test import SimpleTestCase
from django.template import Template, Context


class SupportEmailTagTests(SimpleTestCase):
    def test_returns_mailto_anchor_tag(self):
        emails = (
            ('s@g.com', '&#115;&#64;&#103;&#46;&#99;&#111;&#109'),
            ('support@volla.co', '&#115;&#117;&#112;&#112;&#111;&#114;&#116;'
                                 '&#64;&#118;&#111;&#108;&#108;&#97;&#46;&#99;&#111;'),
        )
        for email, encoded in emails:
            expected = '<a href="mailto:{0}">{0}</a>'.format(encoded)
            with self.settings(SUPPORT_EMAIL=email):
                result = Template(
                    '{% load email %}'
                    '{% email %}'
                ).render(Context())
                self.assertHTMLEqual(result, expected)


