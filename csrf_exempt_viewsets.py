from django.utils.decorators import method_decorator
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class CsrfExemptModelViewSet(viewsets.ModelViewSet):
    pass
