from django.contrib import admin

from .models import Vollume, VollumeChunk


class VollumeAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'created')


admin.site.register(Vollume, VollumeAdmin)
