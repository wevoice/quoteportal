from django.contrib import admin
from . import models
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import ForeignKeyWidget, DecimalWidget
from import_export import fields
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.admin import helpers
from django.template import loader, Context


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
              'get_formatted_vo_prep_value', 'get_formatted_video_loc_value', 'get_formatted_dtp_value',
              'get_formatted_course_build_value', 'get_formatted_course_qa_value',
              'get_formatted_course_finalize_value', 'get_formatted_pm_value', 'get_formatted_total_value',
              'get_tat_value')

    readonly_fields = ('get_formatted_prep_kits_value', 'get_formatted_trans_value', 'get_formatted_mm_prep_value',
                       'get_formatted_vo_prep_value', 'get_formatted_video_loc_value', 'get_formatted_dtp_value',
                       'get_formatted_course_build_value', 'get_formatted_course_qa_value',
                       'get_formatted_course_finalize_value', 'get_formatted_pm_value', 'get_formatted_total_value',
                       'get_tat_value')

    extra = 1

    def translation(self):
        return "$%s" % self.translation if self.translation else ""


class ScopingAdmin(admin.ModelAdmin):
    inlines = [PricingInline, ]
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
    save_on_top = True

    # Show or hide delete action depending on user
    def get_actions(self, request):
        actions = super(ScopingAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    # def get_list_editable(self, request):
    #     actions = super(ScopingAdmin, self).get_actions(request)
    #     if not request.user.is_superuser:
    #         global list_editable
    #         list_editable = None
    #         if 'delete_selected' in actions:
    #             del actions['delete_selected']
    #     return actions, list_editable

    def change_view(self, request, object_id, form_url='', extra_context=None):
        editable = True

        if (not editable) and (not request.user.is_superuser) and request.method == 'POST':
            return HttpResponseForbidden("You do not have permissions to change this estimate")

        more_context = {
            # set a context var telling our customized template to suppress the Save button group
            'my_editable': editable,
        }
        more_context.update(extra_context or {})
        return super(ScopingAdmin, self).change_view(request, object_id, form_url, more_context)

    def response_change(self, request, obj):
        if request.is_ajax() and ('_languageupdate' in request.POST and request.POST['_languageupdate'] == '1'):
            # get all possible inlines for the parent Admin
            inline = None
            formset = None
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets_with_inlines(request, obj),
                                       self.get_inline_instances(request)):
                # get the inline of interest and generate it's formset
                if isinstance(inline, PricingInline):
                    prefix = FormSet[0].get_default_prefix()
                    prefixes[prefix] = prefixes.get(prefix, 0) + 1
                    if prefixes[prefix] != 1 or not prefix:
                        prefix = "%s-%s" % (prefix, prefixes[prefix])
                    formset = FormSet[0](instance=obj, prefix=prefix)

            # get possible fieldsets, readonly, and prepopulated information for the parent Admin
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))

            # generate the inline formset
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets, prepopulated, readonly,
                                                              model_admin=self)

            # render the template
            t = loader.get_template('admin/edit_inline/tabular.html')
            c = Context({'inline_admin_formset': inline_admin_formset})
            rendered_inline_form = t.render(c)
            return JsonResponse({'status': 'languages updated!', 'inline_form': rendered_inline_form})
        return super(ScopingAdmin, self).response_change(request, obj)

    class Media:
        def __init__(self):
            pass
        js = ('portal/admin/js/admin_list_editable_autosubmit.js',
              'portal/admin/js/formset_handlers.js')
        css = {'all': ('portal/admin/css/scoping.css', )}


admin.site.register(models.Scoping, ScopingAdmin)
