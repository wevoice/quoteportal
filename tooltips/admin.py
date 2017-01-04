from django.contrib import admin
from .models import Tooltip


class TooltipAdmin(admin.ModelAdmin):
    list_display = ['url', 'selector', 'title']
    search_fields = ['title', 'url']

admin.site.register(Tooltip, TooltipAdmin)
