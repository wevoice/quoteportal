from django.contrib import admin
from . import models
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import ForeignKeyWidget, DecimalWidget
from import_export import fields
from django.http import JsonResponse
from django.contrib.admin import helpers
from django.template import loader, Context
from django import forms
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import HttpResponseRedirect


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


class PricingInlineForm(forms.ModelForm):
    def clean(self):
        if self.is_valid():
            for attribute in ['embedded_video_time', 'narration_time', 'course_play_time',
                              'video_count', 'linked_resources']:
                if getattr(self.cleaned_data.get('scoping'), attribute) is None:
                    setattr(self.cleaned_data.get('scoping'), attribute, 0)
        return self.cleaned_data


class PricingInline(admin.TabularInline):
    model = models.Pricing
    extra = 1
    form = PricingInlineForm

    fields = ['language', ]
    readonly_fields = []

    # def get_formset(self, request, obj=None, **kwargs):
    #     pets = ((0, 'Dogs'), (1, 'Cats'))
    #     wildanimals = ((0, 'Lion'), (1, 'Tiger'))
    #     # Break this line appart to add your own dict of form fields.
    #     # Also a handy not is you have an instance of the parent object in obj
    #     PricingInline.form = type('PricingFormAlt', (PricingInlineForm,),
    #                               {'pets_select': forms.ChoiceField(label="Pets", choices=pets),
    #                                'get_formatted_prep_kits_value': forms.CharField(label="Prep Kits"),
    #                                'get_formatted_trans_value': forms.CharField(label="Translation"),})
    #     formset = super(PricingInline, self).get_formset(request, obj, **kwargs)
    #     return formset

    def get_formatted_prep_kits_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_prep_kits_value()))
    get_formatted_prep_kits_value.short_description = 'Prep Kits'

    def get_formatted_trans_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_trans_value()))
    get_formatted_trans_value.short_description = 'Translation'

    def get_formatted_mm_prep_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_mm_prep_value()))
    get_formatted_mm_prep_value.short_description = 'MM Prep'

    def get_formatted_vo_prep_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_vo_prep_value()))
    get_formatted_vo_prep_value.short_description = 'VO Prep'

    def get_formatted_video_loc_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_video_loc_value()))
    get_formatted_video_loc_value.short_description = 'Video Loc'

    def get_formatted_dtp_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_dtp_value()))
    get_formatted_dtp_value.short_description = 'DTP'

    def get_formatted_course_build_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_course_build_value()))
    get_formatted_course_build_value.short_description = 'Course Build'

    def get_formatted_course_qa_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_course_qa_value()))
    get_formatted_course_qa_value.short_description = 'Course QA'

    def get_formatted_course_finalize_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_course_finalize_value()))
    get_formatted_course_finalize_value.short_description = 'Course Finalize'

    def get_formatted_pm_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_pm_value()))
    get_formatted_pm_value.short_description = 'PM'

    def get_formatted_total_value(self, obj):
        return "$%s" % intcomma('{0:.2f}'.format(obj.get_total_value()))
    get_formatted_total_value.short_description = 'Total'

    def get_formatted_tat_value(self, obj):
        return "%s" % intcomma('{0:.2f}'.format(obj.get_tat_value()))
    get_formatted_tat_value.short_description = 'TAT'


class DynamicPricingInline(PricingInline):
    def get_fields(self, request, obj=None):
        # retrieve current fields
        target_fields = super(DynamicPricingInline, self).get_fields(request, obj)
        # Filter list of column fields based on current context
        return self.filter_fields(target_fields, obj, read_only=False)

    def get_readonly_fields(self, request, obj=None):
        # retrieve current readonly fields
        target_fields = super(DynamicPricingInline, self).get_readonly_fields(request, obj)
        # Filter list of read-only column fields based on current context
        return self.filter_fields(target_fields, obj)

    def filter_fields(self, target_fields, obj, read_only=True):
        # Reset target column fields list to empty
        target_fields[:] = []
        # Maps UI columns to their data inputs in scoping object fields
        requirements_dict = {}
        # Prep Kits
        requirements_dict.setdefault('course_play_time', []).append('prep_kits')
        # Translation
        requirements_dict.setdefault('total_words', []).append('translation')
        # MM Prep
        requirements_dict.setdefault('video_count', []).append('mm_prep')
        requirements_dict.setdefault('narration_time', []).append('mm_prep')
        # VO Prep
        requirements_dict.setdefault('narration_time', []).append('vo_prep')
        # Video Loc
        requirements_dict.setdefault('ost_elements', []).append('video_loc')
        requirements_dict.setdefault('video_count', []).append('video_loc')
        # DTP
        requirements_dict.setdefault('linked_resources', []).append('dtp')
        # Course Build
        requirements_dict.setdefault('course_play_time', []).append('course_build')
        requirements_dict.setdefault('narration_time', []).append('course_build')
        # Course QA
        requirements_dict.setdefault('course_play_time', []).append('course_qa')

        # Maps UI columns to the functions that calculate their value
        # See above PricingInline class and models Pricing class for functions
        columns_list = [('prep_kits', 'get_formatted_prep_kits_value'),
                        ('translation', 'get_formatted_trans_value'),
                        ('mm_prep', 'get_formatted_mm_prep_value'),
                        ('vo_prep', 'get_formatted_vo_prep_value'),
                        ('video_loc', 'get_formatted_video_loc_value'),
                        ('dtp', 'get_formatted_dtp_value'),
                        ('course_build', 'get_formatted_course_build_value'),
                        ('course_qa', 'get_formatted_course_qa_value'),
                        ('course_finalize', 'get_formatted_course_finalize_value'),
                        ('pm', 'get_formatted_pm_value'),
                        ('total', 'get_formatted_total_value'),
                        ('tat', 'get_formatted_tat_value')]

        columns_dict = dict(columns_list)

        # At runtime, filters UI columns to include only those connected to Scoping fields with values
        for field in obj._meta.get_fields():
            if field.name in requirements_dict and getattr(obj, field.name) > 0:
                requirements = requirements_dict[field.name]
                for item in requirements:
                    requirement = columns_dict[item]
                    if requirement not in target_fields:
                        target_fields.append(requirement)

        # Automatically show PM, Total and TAT columns when columns (other than language column) exist
        if len(target_fields) > 1:
            target_fields.append(columns_dict['pm'])
            target_fields.append(columns_dict['total'])
            target_fields.append(columns_dict['tat'])

        # Show COURSE FINALIZE column only when there are course-related columns
        course_items = dict(columns_list[2:8]).values()
        has_course = any((True for field in target_fields if field in course_items))
        if 'get_formatted_course_finalize_value' not in target_fields and has_course:
            target_fields.append('get_formatted_course_finalize_value')

        # All columns except LANGUAGE will be read-only
        if read_only:
            sorted_target_fields = []
        else:
            sorted_target_fields = ['language']

        for item in columns_list:
            if item[1] in target_fields:
                sorted_target_fields.append(item[1])

        return sorted_target_fields


class ScopingAdmin(admin.ModelAdmin):
    inlines = [DynamicPricingInline, ]

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

    # Show or hide delete action depending on user
    def get_actions(self, request):
        actions = super(ScopingAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

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

        if not request.is_ajax() and "_save" in request.POST:
            return HttpResponseRedirect("../../%s" % obj.id)

        return super(ScopingAdmin, self).response_change(request, obj)

    class Media:
        def __init__(self):
            pass
        js = ('portal/admin/js/admin_list_editable_autosubmit.js',
              'portal/admin/js/formset_handlers.js')
        css = {'all': ('portal/admin/css/scoping.css', )}


admin.site.register(models.Scoping, ScopingAdmin)
