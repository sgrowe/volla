from unittest import TestCase
from unittest.mock import Mock, patch, sentinel
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import ResolverMatch, RegexURLPattern, RegexURLResolver
from simple_urls.resolvers import simple_url, _construct_regex, _validate_path_piece_name, _pattern_for_path_piece
import re


class SimpleUrlTests(TestCase):
    def test_resolves_urls_correctly(self):
        view = Mock()
        url = simple_url('/page/ id: int / title /', view)
        match = url.resolve('page/47/loads-of-info/')
        self.assertIsInstance(match, ResolverMatch)
        self.assertIs(match.func, view)
        self.assertEqual(match.kwargs, {'id': '47', 'title': 'loads-of-info'})
        self.assertEqual(match.args, ())

    @patch('simple_urls.resolvers.url', return_value=sentinel.resolver)
    @patch('simple_urls.resolvers._construct_regex', return_value=sentinel.regex)
    def test_constructed_regex_is_passed_to_django_url(self, construct_regex, django_url):
        view = Mock()
        resolver = simple_url('/home-page/', view, sentinel.kwargs, sentinel.name)
        construct_regex.assert_called_once_with('/home-page/', is_prefix=False)
        django_url.assert_called_once_with(sentinel.regex, view, sentinel.kwargs, sentinel.name)
        self.assertIs(resolver, sentinel.resolver)

    @patch('simple_urls.resolvers._construct_regex', return_value=sentinel.regex)
    def test_detects_include_usage(self, construct_regex):
        include = [Mock(), Mock(), Mock()]
        simple_url('/contact-us/', include, sentinel.kwargs, sentinel.name)
        construct_regex.assert_called_once_with('/contact-us/', is_prefix=True)

    def test_returns_regex_url_pattern_if_passed_view_func(self):
        view = Mock()
        resolver = simple_url('/home-page/', view, sentinel.kwargs, sentinel.name)
        self.assertIsInstance(resolver, RegexURLPattern)

    def test_returns_regex_url_resolver_if_passed_url_includes(self):
        url_includes = (
            (Mock(), Mock(), Mock()),
            [Mock(), Mock(), Mock()],
        )
        for includes in url_includes:
            resolver = simple_url('/home-page/', includes, sentinel.kwargs, sentinel.name)
            self.assertIsInstance(resolver, RegexURLResolver)


class ConstructRegexTests(TestCase):
    def assertRegexMatchesWholeString(self, regex, string, msg=None):
        msg = msg or 'Regex failed to match {!r}'.format(string)
        match = re.match(regex, string)
        self.assertIsNotNone(match, msg)
        self.assertEqual(match.group(), string, msg)

    def assertRegexDoesNotMatch(self, regex, string, msg=None):
        msg = msg or 'Regex should not have matched {!r}'.format(string)
        self.assertIsNone(re.match(regex, string), msg)

    def test_regex_matches_valid_urls(self):
        static_urls = (
            ('/admin/', 'admin/'),
            ('/docs', 'docs'),
            ('/wiffy500/some-page/', 'wiffy500/some-page/'),
            ('/like/8-thousand/pieces/to/the/path', 'like/8-thousand/pieces/to/the/path'),
        )
        dynamic_urls = (
            ('/  page_name  /', 'contact-us/'),
            ('/article/ title', 'article/You-wont_believe-what-happened-next'),
            ('/archive/  old_path: multi  /', 'archive/many/path/pieces/'),
            ('/blog-post/  id: int', 'blog-post/1078'),
            ('/ year: int / month: int / day: int', '1996/08/12'),
            ('/ title / order: int /final', 'something/40/final'),
        )
        for url_pattern, path in static_urls + dynamic_urls:
            regex = _construct_regex(url_pattern, is_prefix=False)
            self.assertRegexMatchesWholeString(regex, path)

    def test_regex_has_named_groups(self):
        urls_and_kwargs = (
            ('/ id: int /', '13/', {'id': '13'}),
            ('/not-a-kwarg/ pk', 'not-a-kwarg/some-thing', {'pk': 'some-thing'}),
            ('/static/only/', 'static/only/', {}),
        )
        for url_pattern, url, kwargs in urls_and_kwargs:
            regex = _construct_regex(url_pattern, is_prefix=False)
            match = re.match(regex, url)
            self.assertEqual(match.groupdict(), kwargs)

    def test_regex_does_not_match_invalid_urls(self):
        bad_urls = (
            ('/stop-extra-stuff/', 'stop-extra-stuff/like-this'),
            ('/no-trailing-slash', 'no-trailing-slash/'),
            ('/user/ username /', 'user/jerry/extra-bits'),
            ('/numbers-only/ pk: int', 'numbers-only/letters'),
            ('/CaseSensitive/', 'casesensitive/'),
            ('/I-like-letters/ chars: alpha', 'I-like-letters/no-sir'),
        )
        for url_pattern, invalid_url in bad_urls:
            regex = _construct_regex(url_pattern, is_prefix=False)
            self.assertRegexDoesNotMatch(regex, invalid_url)

    def test_regex_matches_start_of_url_if_is_prefix_is_true(self):
        valid_urls = (
            ('/the-magic-zone/', 'the-magic-zone/page/1', 'the-magic-zone/', {}),
            ('/dynamic/ bits / num: int', 'dynamic/a-b/19/21/more', 'dynamic/a-b/19', {'bits': 'a-b', 'num': '19'}),
        )
        for url_pattern, path, bit_to_match, groups in valid_urls:
            regex = _construct_regex(url_pattern, is_prefix=True)
            match = re.match(regex, path)
            self.assertIsNotNone(match)
            self.assertEqual(match.group(), bit_to_match)
            self.assertEqual(match.groupdict(), groups)

    def test_regex_only_matches_start_of_url_if_prefix_is_true(self):
            regex = _construct_regex('/about/pages', is_prefix=True)
            self.assertIsNone(re.match(regex, 'other/about/pages'))

    def test_escapes_special_regex_chars_from_static_pieces(self):
        invalid_paths = (
            ('/what?/', '/wha/'),
            ('/repeat+s', '/repeattts'),
        )
        for url, invalid_url in invalid_paths:
            regex = _construct_regex(url, is_prefix=False)
            self.assertRegexDoesNotMatch(regex, invalid_url)

    def test_raises_error_if_no_leading_forward_slash(self):
        with self.assertRaises(ImproperlyConfigured):
            _construct_regex('docs', is_prefix=False)


class ValidatePathPieceNameTests(TestCase):
    def test_allows_valid_names(self):
        valid_names = (
            'words',
            'fjsj',
            'valid_name',
            'UPPER',
        )
        for name in valid_names:
            _validate_path_piece_name(name)

    def test_raises_error_on_invalid_names(self):
        invalid_names = (
            'no spaces',
            "Can'tHavePunctuation",
            '',
            '40',
            'no-thanks',
        )
        for name in invalid_names:
            with self.assertRaises(ImproperlyConfigured, msg='Failed to raise error on {!r}'.format(name)):
                _validate_path_piece_name(name)


class PatternForPathPieceTests(TestCase):
    def test_returns_valid_regex_patterns(self):
        valid_types = (
            '',
            'int',
            'alpha',
            'multi',
        )
        for piece_type in valid_types:
            regex = _pattern_for_path_piece(piece_type)
            re.compile(regex)

    def test_raises_error_on_unknown_types(self):
        invalid_types = (
            'djd',
            'float',
        )
        for piece_type in invalid_types:
            with self.assertRaises(ImproperlyConfigured):
                _pattern_for_path_piece(piece_type)
