from django.contrib import admin
from . import models
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import ForeignKeyWidget, DecimalWidget
from import_export import fields


class ClientAdmin(ImportExportActionModelAdmin):
    list_display = ('id', 'name',)
admin.site.register(models.Client, ClientAdmin)


class LanguageAdmin(ImportExportActionModelAdmin):
    list_display = ('id', 'name',)
admin.site.register(models.Language, LanguageAdmin)


class SlaResource(resources.ModelResource):

    target_language = fields.Field(
        column_name='target_language',
        attribute='target_language',
        widget=ForeignKeyWidget(models.Language, 'name')
    )

    no_match = fields.Field(
        column_name='no_match',
        attribute='no_match',
        widget=DecimalWidget()
    )

    class Meta:
        model = models.Sla
        skip_unchanged = True
        report_skipped = False

        widgets = {
            'created_date': {'format': '%d.%m.%Y'},
            'last_updated': {'format': '%d.%m.%Y'}
        }

        exclude = ("created_date", "last_updated")


class SlaAdmin(ImportExportActionModelAdmin):
    list_display = ('id', 'target_language', 'formatted_no_match', 'fuzzy_95_99', 'fuzzy_85_94', 'fuzzy_lt_84', 'reps',
                    'match_100', 'linguistic_rate', 'qa', 'audio_recording_plain', 'audio_recording_timed', 'pm', 'dtp',
                    'eng', 'mm_eng', 'created_date_tz_aware', 'last_updated_tz_aware')
    list_filter = ('client',)
    resource_class = SlaResource
admin.site.register(models.Sla, SlaAdmin)


class PricingInline(admin.TabularInline):
    model = models.Pricing

    fields = ('language', 'get_formatted_prep_kits_value', 'get_formatted_trans_value', 'get_formatted_mm_prep_value',
              'get_formatted_vo_prep_value', 'get_formatted_video_loc_value', 'dtp', 'course_qa',
              'course_finalize', 'pm', 'total', 'tat')

    readonly_fields = ('get_formatted_prep_kits_value', 'get_formatted_trans_value', 'get_formatted_mm_prep_value',
                       'get_formatted_vo_prep_value', 'get_formatted_video_loc_value', 'dtp', 'course_qa',
                       'course_finalize', 'pm', 'total', 'tat')

    extra = 1

    def translation(self):
        return "$%s" % self.translation if self.translation else ""


class ScopingAdmin(admin.ModelAdmin):
    inlines = (PricingInline,)
    fieldsets = (
        (None, {
            'fields': ('name', 'client', ('course_play_time', 'narration_time', 'embedded_video_time', 'video_count',
                                          'transcription', 'linked_resources'), ('total_words', 'ost_elements'))
        }),
    )
    list_display = ('name', 'course_play_time', 'narration_time', 'embedded_video_time', 'video_count', 'transcription',
                    'linked_resources', 'total_words', 'ost_elements')
    list_editable = ('course_play_time', 'narration_time', 'embedded_video_time', 'video_count', 'transcription',
                     'linked_resources')

    readonly_fields = ('total_words', 'ost_elements')

    actions_on_bottom = True
    actions_on_top = False
    # actions = None

    # Show or hide delete action depending on user
    # def get_actions(self, request):
    #     actions = super(ScopingAdmin, self).get_actions(request)
    #     if request.user.username[0].upper() != 'J':
    #         if 'delete_selected' in actions:
    #             del actions['delete_selected']
    #     return actions


    # def response_add(self, request, obj, post_url_continue=None):
    #     obj = self.after_saving_model_and_related_inlines(obj)
    #     return super(ScopingAdmin, self).response_add(request, obj)
    #
    # def response_change(self, request, obj):
    #     obj = self.after_saving_model_and_related_inlines(obj)
    #     return super(ScopingAdmin, self).response_change(request, obj)
    #
    # def after_saving_model_and_related_inlines(self, obj):
    #     if hasattr(obj, "related_set"):
    #         print(obj.related_set.all())
    #     # now we have what we need here... :)
    #     return obj




    # http://guido.vonrudorff.de/django-admin-post-save-hook-for-foreign-keys-with-inline-forms/
    # def save_related(self, request, form, formsets, change):
    #     # here is the place for pre_save actions - nothing has been written to the database, yet
    #     super(type(self), self).save_related(request, form, formsets, change)
    #     # now you have all objects in the database
    #     if not change:
    #         pass

    class Media:
        def __init__(self):
            pass
        js = ('admin/js/admin_list_editable_autosubmit.js',)
        css = {'all': ('admin/css/scoping.css', )}


admin.site.register(models.Scoping, ScopingAdmin)

