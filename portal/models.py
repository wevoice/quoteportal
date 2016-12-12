from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import get_current_timezone
import datetime
import math
import locale
locale.setlocale(locale.LC_ALL, '')


def localize_datetime(dtime):
    """Makes DateTimeField value UTC-aware and returns datetime string localized
    in user's timezone in ISO format.
    """
    tz_aware = dtime.astimezone(get_current_timezone())
    return datetime.datetime.strftime(tz_aware, '%Y-%m-%d %H:%M:%S')


def mround(x, prec=2, base=.5):
    return round(base * round(float(x)/base), prec)


class Client(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Language(models.Model):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Scoping(models.Model):

    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    client = models.ForeignKey("Client", blank=True, null=True)
    course_play_time = models.IntegerField(blank=True, null=True)
    narration_time = models.IntegerField(blank=True, null=True)
    embedded_video_time = models.IntegerField(blank=True, null=True)
    video_count = models.IntegerField(blank=True, null=True)
    transcription = models.CharField(max_length=8, choices=YES_NO_CHOICES, blank=True, null=True)
    linked_resources = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_words = models.IntegerField(blank=True, null=True)
    ost_elements = models.IntegerField(blank=True, null=True)

    @property
    def created_tz(self):
        return localize_datetime(self.created)

    def get_total_words(self):
        return self.course_play_time * 92 \
                       + self.narration_time * 150 \
                       + self.video_count * 8 \
                       + self.linked_resources * 300

    def get_ost_elements(self):
        return int(self.embedded_video_time * 2.5)

    class Meta:
        verbose_name = "Estimate"
        verbose_name_plural = "Estimates"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.total_words = self.get_total_words()
        self.ost_elements = self.get_ost_elements()
        for pricing_set in self.pricing_set.all():
            pricing_set.save()
        super(Scoping, self).save(*args, **kwargs)


class Pricing(models.Model):
    scoping = models.ForeignKey("Scoping", blank=True, null=True)
    language = models.ForeignKey("Language", blank=True, null=True)
    prep_kits = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    translation = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    mm_prep = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    vo = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    video_loc = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dtp = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    course_build = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    course_qa = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    course_finalize = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    pm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tat = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def created_tz(self):
        return localize_datetime(self.created)

    def get_prep_kits_value(self):
        if self.language.code == 'en-US':
            prep_kits_value = mround((self.scoping.course_play_time * 4.0)/60)*60
        else:
            prep_kits_value = 0.00
        return prep_kits_value

    def get_formatted_prep_kits_value(self):
        return '${0}'.format(self.get_prep_kits_value())
    get_formatted_prep_kits_value.short_description = 'Prep Kits'

    def get_trans_value(self):
        if self.language.code != 'en-US':
            lang = self.language.id
            sla_lang = self.scoping.client.sla_set.filter(target_language_id=lang)
            rate = sla_lang[0].no_match
            translation_value = self.scoping.total_words * float(rate)
        else:
            translation_value = 0.00
        return translation_value

    def get_formatted_trans_value(self):
        return '${0}'.format(self.get_trans_value())
    get_formatted_trans_value.short_description = 'Translation'

    def get_mm_prep_value(self):
        if self.language.code != 'en-US':
            lang = self.language.id
            sla_lang = self.scoping.client.sla_set.filter(target_language_id=lang)
            mm_eng_rate = sla_lang[0].mm_eng
            prep_kits_value = (mround((self.scoping.narration_time * 2.0)/60)*float(mm_eng_rate))\
                + (math.ceil((self.scoping.video_count/5.0))*float(mm_eng_rate))
            if self.scoping.transcription == "Y":
                prep_kits_value += self.scoping.narration_time * 5.0
        else:
            prep_kits_value = 0.00
        return prep_kits_value

    def get_formatted_mm_prep_value(self):
        return '${0}'.format(self.get_mm_prep_value())
    get_formatted_mm_prep_value.short_description = 'MM Prep'

    def get_vo_prep_value(self):
        if self.language.code != 'en-US':
            lang = self.language.id
            sla_lang = self.scoping.client.sla_set.filter(target_language_id=lang)
            vo_rate = sla_lang[0].audio_recording_plain
            vo_prep_value = self.scoping.embedded_video_time * float(vo_rate)
        else:
            vo_prep_value = 0.00
        return vo_prep_value

    def get_formatted_vo_prep_value(self):
        return '${0}'.format(self.get_vo_prep_value())
    get_formatted_vo_prep_value.short_description = 'VO Prep'

    def get_video_loc_value(self):
        if self.language.code != 'en-US':
            lang = self.language.id
            sla_lang = self.scoping.client.sla_set.filter(target_language_id=lang)
            mm_eng_rate = sla_lang[0].mm_eng
            video_loc_value = (mround(self.scoping.ost_elements / 10.0)*float(mm_eng_rate))\
                + float(0.25 * self.scoping.video_count * float(mm_eng_rate))
        else:
            video_loc_value = 0.00
        return video_loc_value

    def get_formatted_video_loc_value(self):
        return '${0}'.format(self.get_video_loc_value())
    get_formatted_video_loc_value.short_description = 'Video Loc'

    def save(self, *args, **kwargs):
        self.prep_kits = self.get_prep_kits_value()
        self.translation = self.get_trans_value()
        self.mm_prep = self.get_mm_prep_value()
        super(Pricing, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Pricing Per Language"
        unique_together = ('scoping', 'language',)

    def __unicode__(self):
        return str(self.language)


class Sla(models.Model):
    client = models.ForeignKey("Client", blank=True, null=True)
    target_language = models.ForeignKey("Language", blank=True, null=True)
    no_match = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fuzzy_95_99 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fuzzy_85_94 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fuzzy_lt_84 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    reps = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    match_100 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    linguistic_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    qa = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    audio_recording_plain = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    audio_recording_timed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    pm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dtp = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    eng = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    mm_eng = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def created_date_tz_aware(self):
        return localize_datetime(self.created_date)
    created_date_tz_aware.short_description = 'Created Date'

    def last_updated_tz_aware(self):
        return localize_datetime(self.created_date)
    last_updated_tz_aware.short_description = 'Last Updated'

    def formatted_no_match(self):
        return '${0}'.format(self.no_match)
    formatted_no_match.short_description = 'No Match'

    class Meta:
        verbose_name_plural = "SLA By Client"
        ordering = ['target_language__name']
        unique_together = ('client', 'target_language',)

    def __unicode__(self):
        return self.target_language.name
