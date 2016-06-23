from django.test import SimpleTestCase
from unittest.mock import Mock
from django.core.exceptions import ValidationError
from django.http import Http404
from form_helpers import show_validation_errors_in_form


class ShowValidationErrorsInFormTests(SimpleTestCase):
    def test_catches_validation_errors(self):
        form = Mock()
        with show_validation_errors_in_form(form):
            error_dict = {None: 'This error should have been caught by "show_validation_errors_in_form".'}
            raise ValidationError(error_dict)

    def test_does_not_catch_other_errors(self):
        for exception in (Exception, Http404, KeyError):
            form = Mock()
            with self.assertRaises(exception):
                with show_validation_errors_in_form(form):
                    raise exception()

    def test_adds_validation_errors_to_given_form(self):
        form = Mock()
        errors = (
            (None, 'A non-field error'),
            ('title', 'The title is ALL WRONG!'),
            ('data', "something ain't right man"),
        )
        with show_validation_errors_in_form(form):
            raise ValidationError(dict(errors))
        for field, message in errors:
            form.add_error.assert_any_call(field, [message])
