from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from form_helpers import show_validation_errors_in_form
from users.helpers import url_for_auth_view_which_returns_to_here
import logging


logger = logging.getLogger('volla.vollumes')


class CreateVollumeForm(forms.Form):
    title = forms.CharField(required=True)
    text = forms.CharField(widget=forms.Textarea, required=True)


class NewParagraphForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=True)


def handle_new_paragraph_form(request, parent_paragraph):
    """
    Handles requests to views using NewParagraphForm, returning either an instance of the form or a HTTP redirect
    as needed.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated():
            login_url = url_for_auth_view_which_returns_to_here('login', request)
            return HttpResponseRedirect(login_url)
        form = NewParagraphForm(request.POST)
        if form.is_valid():
            with show_validation_errors_in_form(form):
                new_para = parent_paragraph.add_child(
                    author=request.user,
                    text=form.cleaned_data['text']
                )
                logger.info(
                    'New paragraph for vollume "%s" created by user %s',
                    parent_paragraph.vollume,
                    new_para.author
                )
                return redirect(new_para)
    else:
        form = NewParagraphForm()
    return form
