from simple_urls import simple_url as url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from vollumes.views import home, vollume_start, new_vollume, vollume_page, WelcomeView, user_profile
from users.views import register


def auth_form_view(title, target, submit_button_text=None):
    return {
        'template_name': 'volla/form_view.html',
        'extra_context': {
            'title': title,
            'form_target': target,
            'submit_button_text': submit_button_text or title,
        },
    }


urlpatterns = [
    url('/', home, name='home'),
    url('/welcome/', WelcomeView.as_view(), name='welcome-tour'),
    # Vollumes
    url('/new-vollume/', new_vollume, name='new-vollume'),
    url('/vollume/ vollume_id /', vollume_start, name='vollume'),
    url('/vollume/ vollume_id / paragraph_id /', vollume_page, name='vollume-page'),
    # Users
    url('/user/ user_id /', user_profile, name='user'),
    # User actions
    url('/sign-up/', register, name='register'),
    url('/login/', login, auth_form_view('Login', 'login'), name='login'),
    url('/logout/', logout, {'next_page': '/'}, name='logout'),
    # Admin
    url('/super-secret-zone/admin/', admin.site.urls),
]
