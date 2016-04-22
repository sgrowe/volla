from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from vollumes.views import VollumeViewSet, ParagraphViewSet
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'vollumes', VollumeViewSet)
router.register(r'paragraphs', ParagraphViewSet, base_name='paragraph')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^super-secret-zone/', include([
        url(r'^admin/', admin.site.urls),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ])),
]
