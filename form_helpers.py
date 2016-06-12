from django.core.exceptions import ValidationError


class AddValidationErrorsToForm:
    def __init__(self, form):
        self.form = form

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is ValidationError:
            for field, message in exc_val.message_dict.items():
                self.form.add_error(field, message)
            return True


def show_validation_errors_in_form(form):
    return AddValidationErrorsToForm(form)
