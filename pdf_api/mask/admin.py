from django.contrib import admin

from .models import MaskRequest, MaskResult

admin.site.register(MaskRequest)
admin.site.register(MaskResult)
