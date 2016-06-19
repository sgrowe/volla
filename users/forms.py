from django import forms
from django.contrib.auth.password_validation import validate_password
from users.models import User


class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email')

    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])
    password_repeat = forms.CharField(widget=forms.PasswordInput)

    sensitive_parameters = ('password', 'password_repeat')

    def clean(self):
        cleaned_data = super().clean()
        self.ensure_password_fields_match(cleaned_data)
        return cleaned_data

    def ensure_password_fields_match(self, cleaned_data):
        if cleaned_data.get('password') != cleaned_data.get('password_repeat'):
            self.add_error('password_repeat', 'The passwords do not match.')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
