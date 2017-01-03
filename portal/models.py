from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
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


def roundup(x):
    return math.ceil(x / 10.0) * 10


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


class DTPAsset(models.Model):
    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )

    name = models.CharField(max_length=128)
    scoping = models.ForeignKey("Scoping")
    total_pages = models.IntegerField(blank=True, null=True, default=0)
    total_wordcount = models.IntegerField(blank=True, null=True, default=0)
    editable_source_available = models.CharField(max_length=16, choices=YES_NO_CHOICES, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "DTP Assets"


class Scoping(models.Model):

    YES_NO_CHOICES = (
        ("Y", "Yes"),
        ("N", "No")
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    client = models.ForeignKey("Client", blank=True, null=True)
    course_play_time = models.IntegerField(blank=True, null=True, default=0)
    narration_time = models.IntegerField(blank=True, null=True, default=0)
    embedded_video_time = models.IntegerField(blank=True, null=True, default=0)
    video_count = models.IntegerField(blank=True, null=True, default=0)
    transcription = models.CharField(max_length=8, choices=YES_NO_CHOICES, blank=True, null=True, default="N")
    linked_resources = models.IntegerField(blank=True, null=True, default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_words = models.IntegerField(blank=True, null=True)
    ost_elements = models.IntegerField(blank=True, null=True)

    @property
    def created_tz(self):
        return localize_datetime(self.created)

    def get_total_words(self):
        dtp_assets = self.dtpasset_set.aggregate(Sum('total_pages'))['total_pages__sum']
        return math.ceil(sum([(self.course_play_time * 92), (self.narration_time * 150), (self.embedded_video_time * 8),
                             (dtp_assets * 300)]))
        #  return math.ceil(sum([(self.course_play_time * 92), (self.narration_time * 150), (self.embedded_video_time * 8),
        #                      (self.linked_resources * 300)]))

    def get_ost_elements(self):
        return math.ceil(self.embedded_video_time * 2.5)

    class Meta:
        verbose_name = "Estimate"
        verbose_name_plural = "Estimates"
        unique_together = ('name', 'client',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.total_words = self.get_total_words()
        self.ost_elements = self.get_ost_elements()
        for pricing_set in self.pricing_set.all():
            pricing_set.save()
        super(Scoping, self).save(*args, **kwargs)


@receiver(post_save, sender=Scoping)
def create_source_language(sender, instance, created, **kwargs):
    if created and instance.pricing_set.count() == 0:
        language = Language.objects.get(code='en-US')
        pricing = Pricing.objects.create(scoping=instance, language=language)
        pricing.save()


class PricingValue(object):
    def __init__(self, pricing):
        self.pricing = pricing
        self.sla_lang = self.get_sla_lang()
        self.prep_kits_value = self.get_prep_kits_value()
        self.translation_value = self.get_translation_value()
        self.mm_prep_value = self.get_mm_prep_value()
        self.vo_prep_value = self.get_vo_prep_value()
        self.video_loc_value = self.get_video_loc_value()
        self.dtp_value = self.get_dtp_value()
        self.course_build_value = self.get_course_build_value()
        self.course_qa_value = self.get_course_qa_value()
        self.course_finalize_value = self.get_course_finalize_value()
        self.pm_value = self.get_pm_value()
        self.total_value = self.get_total_value()
        self.tat_value = self.get_tat_value()

    def get_sla_lang(self):
        if self.pricing.language.code != 'en-US':
            lang = self.pricing.language.id
            sla_lang = self.pricing.scoping.client.sla_set.filter(target_language_id=lang)[0]
        else:
            sla_lang = None
        return sla_lang

    def get_prep_kits_value(self):
        if self.sla_lang:
            return mround((self.pricing.scoping.course_play_time * 4.0)/60)*60
        return 0.00

    def get_translation_value(self):
        if self.sla_lang:
            rate = self.sla_lang.no_match
            return self.pricing.scoping.total_words * float(rate)
        return 0.00

    def get_mm_prep_value(self):
        if self.sla_lang:
            rate = self.sla_lang.mm_eng
            value = (mround((self.pricing.scoping.narration_time * 2.0) / 60) * float(rate)) \
                + (math.ceil((self.pricing.scoping.video_count / 5.0)) * float(rate))
            if self.pricing.scoping.transcription == "Y":
                value += self.pricing.scoping.narration_time * 5.0
            return value
        return 0.00

    def get_vo_prep_value(self):
        if self.sla_lang:
            rate = self.sla_lang.audio_recording_plain
            return self.pricing.scoping.narration_time * float(rate)
        return 0.00

    def get_video_loc_value(self):
        if self.sla_lang:
            rate = self.sla_lang.mm_eng
            return (mround(self.pricing.scoping.ost_elements / 10.0, prec=2, base=1) * float(rate)) \
                + float(0.25 * self.pricing.scoping.video_count * float(rate))
        return 0.00

    def get_dtp_value(self):
        if self.sla_lang:
            dtp_assets = self.pricing.scoping.dtpasset_set.aggregate(Sum('total_pages'))['total_pages__sum']
            rate = self.sla_lang.dtp
            # return mround(self.pricing.scoping.linked_resources / 15.0)*float(rate)
            return mround(dtp_assets / 15.0)*float(rate)
        return 0.00

    def get_course_build_value(self):
        if self.sla_lang:
            rate = self.sla_lang.mm_eng
            return mround(self.pricing.scoping.course_play_time / 15.0
                          + self.pricing.scoping.narration_time / 10.0, prec=2, base=1) * float(rate)
        return 0.00

    def get_course_qa_value(self):
        if self.sla_lang:
            rate = self.sla_lang.qa
            return mround(self.pricing.scoping.course_play_time * 5.0/60) * float(rate)
        return 0.00

    def get_course_finalize_value(self):
        if self.sla_lang:
            return sum([self.get_mm_prep_value(), self.get_vo_prep_value(), self.get_video_loc_value(),
                        self.get_dtp_value(), self.get_course_build_value(), self.get_course_qa_value()]) * 0.25
        return 0.00

    def get_pm_value(self):
        if self.sla_lang:
            rate = self.sla_lang.pm
            base_value = sum([self.get_translation_value(), self.get_mm_prep_value(), self.get_vo_prep_value(),
                              self.get_video_loc_value(), self.get_dtp_value(), self.get_course_build_value(),
                              self.get_course_qa_value(), self.get_course_finalize_value()]) * float(rate)
            value = float(format(base_value, '.2f'))
        else:
            value = float(format(self.get_prep_kits_value() * .08, '.2f'))
        return value

    def get_total_value(self):
        if self.sla_lang:
            value = sum([self.get_translation_value(), self.get_mm_prep_value(), self.get_vo_prep_value(),
                         self.get_video_loc_value(), self.get_dtp_value(), self.get_course_build_value(),
                         self.get_course_qa_value(), self.get_course_finalize_value(), self.get_pm_value()])
        else:
            value = sum([self.get_prep_kits_value(), self.get_pm_value()])
        return value

    def get_tat_value_base(self, tat_unit):
        tat_value = 3
        if tat_unit < 120:
            tat_value = 1
        elif tat_unit < 180:
            tat_value = 2
        return tat_value

    def get_tat_value(self):
        if self.sla_lang:
            tat_value = 3
            if self.pricing.scoping.course_play_time < 180:
                tat_value = 1
            elif self.pricing.scoping.course_play_time < 360:
                tat_value = 2
        else:
            tat_value = math.ceil(sum([self.pricing.scoping.total_words / 2000,
                                       6,
                                       self.get_tat_value_base(self.pricing.scoping.embedded_video_time),
                                       math.ceil(self.pricing.scoping.course_play_time / 15),
                                       2]) * 1.2)
        return tat_value


class Pricing(models.Model):
    scoping = models.ForeignKey("Scoping", blank=True, null=True)
    language = models.ForeignKey("Language", blank=True, null=True)
    prep_kits = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    translation = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mm_prep = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    video_loc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dtp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_build = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_qa = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    course_finalize = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def created_tz(self):
        return localize_datetime(self.created)

    @property
    def values(self):
        return PricingValue(self)

    def save(self, *args, **kwargs):
        self.prep_kits = self.values.prep_kits_value
        self.translation = self.values.translation_value
        self.mm_prep = self.values.mm_prep_value
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
