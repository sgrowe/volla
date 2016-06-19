from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from users.forms import RegisterForm


def set_logged_in_user(request, username, password):
    user = authenticate(username=username, password=password)
    login(request, user)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username, password = (form.cleaned_data[key] for key in ('username', 'password'))
            set_logged_in_user(request, username, password)
            return redirect(reverse('home'))
    else:
        form = RegisterForm()
    context = {
        'form': form,
        'form_target': 'register',
        'title': 'Sign up',
        'submit_button_text': 'Sign up',
    }
    return render(request, 'volla/form_view.html', context)
