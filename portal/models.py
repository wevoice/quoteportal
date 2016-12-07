from __future__ import unicode_literals

from django.db import models
from django.db import models as dbmodels
from django.forms import Textarea
from django.utils.timezone import get_current_timezone, make_aware, utc
import datetime


def localize_datetime(dtime):
    """Makes DateTimeField value UTC-aware and returns datetime string localized
    in user's timezone in ISO format.
    """
    tz_aware = make_aware(dtime, utc).astimezone(get_current_timezone())
    return datetime.datetime.strftime(tz_aware, '%Y-%m-%d %H:%M:%S')


class Client(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class AudioAsset(models.Model):
    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    name = models.CharField(max_length=128)
    ts_request = models.ForeignKey("Request")
    transcription = models.CharField(max_length=16, choices=YES_NO_CHOICES, blank=True, null=True)
    path_to_source = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Audio"


class DTPAsset(models.Model):
    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    PLATFORM_CHOICES = (
        ("M", "Mac"),
        ("W", "Windows"),
        ("E", "Either")
    )

    name = models.CharField(max_length=128)
    ts_request = models.ForeignKey("Request")
    dtp_application = models.CharField(max_length=256, blank=True, null=True)
    mac_or_windows = models.CharField(max_length=32, choices=PLATFORM_CHOICES, blank=True, null=True)
    lso_on_dtp = models.CharField(max_length=16, choices=YES_NO_CHOICES)
    path_to_source = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "DTP"


class VideoAsset(models.Model):
    DUB_CHOICES = (
        ("DUB", "Dubbing"),
        ("SUB", "Subtitle")
    )

    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    name = models.CharField(max_length=128)
    ts_request = models.ForeignKey("Request")
    dub_or_subtitle = models.CharField(max_length=128, choices=DUB_CHOICES, blank=True, null=True)
    onscreen_text = models.CharField(max_length=16, choices=YES_NO_CHOICES, blank=True, null=True)
    transcription = models.CharField(max_length=16, choices=YES_NO_CHOICES, blank=True, null=True)
    path_to_source = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Video"


class GraphicAsset(models.Model):
    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    name = models.CharField(max_length=128)
    ts_request = models.ForeignKey("Request")
    editable_graphics_source_available = models.CharField(max_length=16, choices=YES_NO_CHOICES, blank=True, null=True)
    path_to_source = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Graphics"


class PDFAsset(models.Model):
    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    name = models.CharField(max_length=128)
    ts_request = models.ForeignKey("Request")
    editable_pdf_source_available = models.CharField(max_length=16, choices=YES_NO_CHOICES, blank=True, null=True)
    path_to_source = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "PDFs"


class Request(models.Model):
    formfield_overrides = {
        dbmodels.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 25})},
    }

    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    NUMBER_CHOICES = (
        ("None", "None"),
        ("One", "One"),
        ("Two", "Two"),
        ("Three", "Three")
    )

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("PROD", "Production"),
        ("COMP", "Completed"),
        ("CLOSED", "Closed"),
        ("HOLD", "On Hold")
    )

    TMS_CHOICES = (
        ("GS", "GlobalSight"),
        ("IWS", "Idiom WorldServer (versions 8.x)"),
        ("SDL_TMS", "SDL TMS"),
        ("SDL_GS", "SDL GroupShare"),
        ("GL", "GlobalLink"),
        ("SL", "Smartlink"),
        ("TF", "Transifex"),
        ("XTM", "XTM"),
        ("Plunet", "Plunet"),
        ("GTT", "GTT"),
        ("CW", "Cloudwords"),
        ("Asterix", "Asterix"),
        ("MQ", "MemoQ Server"),
        ("MC", "MateCat"),
        ("Other", "Other")
    )
    name = models.CharField(max_length=128)
    client = models.ForeignKey("Client")
    new_account = models.BooleanField()
    tms_or_cat_tool = models.CharField(max_length=128, choices=TMS_CHOICES, default="GS", blank=True, null=True,
                                       verbose_name="TMS or CAT tool used")
    tms_login_info = models.CharField(max_length=256, blank=True, null=True, verbose_name="TMS login info")
    path_to_source = models.CharField(max_length=128, blank=True, null=True)
    source_language = models.ForeignKey("Language", related_name="sourcelanguage", default=5, blank=True, null=True)
    target_languages = models.ManyToManyField("Language")
    sla_metrics_path = models.CharField(max_length=128, blank=True, null=True, verbose_name="SLA metrics path")
    rounds_of_testing = models.CharField(max_length=8, choices=NUMBER_CHOICES, blank=True, null=True)
    project_and_filetype_info = models.TextField(blank=True, null=True)
    client_instructions = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    requested_due_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default="OPEN", blank=True, null=True)

    @property
    def created_tz(self):
        return localize_datetime(self.created)

    def __unicode__(self):
        return self.name
