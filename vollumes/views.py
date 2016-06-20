from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from users.models import User
from vollumes.models import Vollume, create_validate_and_save_vollume, get_paragraph_or_404
from form_helpers import show_validation_errors_in_form


def home(request):
    context = {
        'whole-title': 'Volla - Social story writing',
        'vollumes': Vollume.objects.all(),
    }
    return render(request, 'vollumes/home.html', context)


class WelcomeView(TemplateView):
    template_name = 'volla/welcome-tour.html'


class CreateVollumeForm(forms.Form):
    title = forms.CharField(required=True)
    text = forms.CharField(widget=forms.Textarea, required=True)


@login_required()
def new_vollume(request):
    if request.method == 'POST':
        form = CreateVollumeForm(request.POST)
        if form.is_valid():
            with show_validation_errors_in_form(form):
                vollume = create_validate_and_save_vollume(
                    author=request.user,
                    title=form.cleaned_data['title'],
                    text=form.cleaned_data['text']
                )
                return redirect(vollume)
    else:
        form = CreateVollumeForm()
    context = {
        'form': form,
        'form_target': 'new-vollume',
        'submit_button_text': 'Create',
        'title': 'Start a new vollume',
    }
    return render(request, 'volla/form_view.html', context)


def vollume_start(request, vollume_id):
    vollume = Vollume.get_by_hashid_or_404(vollume_id)
    context = {
        'vollume': vollume,
        'title': vollume.title,
        'paragraphs': [vollume.first_paragraph],
    }
    return render(request, 'vollumes/vollume.html', context)


class NewParagraphForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=True)


def handle_new_paragraph_form(request, parent_paragraph):
    """
    Handles requests to views using NewParagraphForm, returning either an instance of the form or a HTTP redirect
    as needed.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated():
            login_url = '{}?next={}'.format(reverse('login'), request.build_absolute_uri())
            return HttpResponseRedirect(login_url)
        form = NewParagraphForm(request.POST)
        if form.is_valid():
            with show_validation_errors_in_form(form):
                new_para = parent_paragraph.add_child(
                    author=request.user,
                    text=form.cleaned_data['text']
                )
                return redirect(new_para.get_absolute_url())
    else:
        form = NewParagraphForm()
    return form


def vollume_page(request, vollume_id, paragraph_id):
    parent_paragraph = get_paragraph_or_404(vollume_id, paragraph_id)
    form_or_redirect = handle_new_paragraph_form(request, parent_paragraph)
    if isinstance(form_or_redirect, HttpResponseRedirect):
        return form_or_redirect
    else:
        form = form_or_redirect
    context = {
        'vollume': parent_paragraph.vollume,
        'title': parent_paragraph.vollume.title,
        'paragraphs': parent_paragraph.children.all(),
        'form': form,
        'form_submit_url': request.path,
    }
    return render(request, 'vollumes/vollume.html', context)


def user_profile(request, user_id):
    user = User.get_by_hashid_or_404(user_id)
    context = {
        'title': 'User {}'.format(user.username),
        'user': user,
    }
    return render(request, 'vollumes/user.html', context)
