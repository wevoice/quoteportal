from django.db import models


class Tooltip(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=255, db_index=True)
    selector = models.CharField(max_length=50, default='', blank=False, null=False, help_text='div:contains("example")')
    title = models.CharField(max_length=255)
    body = models.TextField()
