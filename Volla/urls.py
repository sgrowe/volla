from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from stories.views import VollumeViewSet, VollumeStructureViewSet, ParaViewSet
from users.views import UserViewSet, get_current_user, login_view, logout_view

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'vollumes', VollumeViewSet)
router.register(r'vollume-structures', VollumeStructureViewSet)
router.register(r'paragraphs', ParaViewSet)

api_urls = router.urls

api_urls.append(url(r'^session/', include([
    url(r'^$', get_current_user, name="current-user"),
    url(r'^login/$', login_view, name="login"),
    url(r'^logout/$', logout_view, name="logout"),
])))

urlpatterns = [
    url(r'^api/', include(api_urls)),
    url(r'^super-secret-zone/', include([
        url(r'^admin/', admin.site.urls),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ])),
]
