from django.contrib import admin
from . import models

from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields


class VideoAssetInline(admin.StackedInline):
    model = models.VideoAsset
    extra = 0


class AudioAssetInline(admin.StackedInline):
    model = models.AudioAsset
    extra = 0


class DTPAssetInline(admin.StackedInline):
    model = models.DTPAsset
    extra = 0


class GraphicAssetInline(admin.StackedInline):
    model = models.GraphicAsset
    extra = 0


class ClientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'name',)
admin.site.register(models.Client, ClientAdmin)


class LanguageAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'name',)
admin.site.register(models.Language, LanguageAdmin)


class RequestResource(resources.ModelResource):

    client = fields.Field(
        column_name='client',
        attribute='client',
        widget=ForeignKeyWidget(models.Client, 'name')
    )

    source_language = fields.Field(
        column_name='source_language',
        attribute='source_language',
        widget=ForeignKeyWidget(models.Language, 'name')
    )

    languages = fields.Field(
        column_name='target_languages',
        attribute='target_languages',
        widget=ManyToManyWidget(models.Language, ",", "name")
    )

    class Meta:
        model = models.Request
        skip_unchanged = True
        report_skipped = False

        widgets = {
            'created_date': {'format': '%d.%m.%Y'},
            'requested_due_date': {'format': '%d.%m.%Y'}
        }

        # fields = ('id', 'name', 'client', 'new_account', 'tms_or_cat_tool', 'tms_login_info', 'path_to_source',
        #           'source_language', 'languages', 'rounds_of_testing', 'project_and_filetype_info',
        #           'client_instructions', 'created_date', 'requested_due_date', 'status')
        #
        # export_order = ('id', 'name', 'client', 'new_account', 'tms_or_cat_tool', 'tms_login_info', 'path_to_source',
        #                 'source_language', 'languages', 'rounds_of_testing', 'project_and_filetype_info',
        #                 'client_instructions', 'created_date', 'requested_due_date', 'status')

        fields = ('id', 'name', 'client', 'created_date')
        export_order = ('id', 'name', 'client', 'created_date')

    def for_delete(self, row, instance):
        return self.fields['name'].clean(row) == ''

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        dataset = dataset
        return dataset

    def before_export(self, queryset, *args, **kwargs):
        queryset = queryset.filter(client__name="Gillette")
        return queryset

    def after_export(self, queryset, data, *args, **kwargs):
        pass


class RequestAdmin(ImportExportActionModelAdmin):
    list_filter = ('client', 'status')
    inlines = [VideoAssetInline, AudioAssetInline, DTPAssetInline, GraphicAssetInline]
    list_display = ('id', 'name', 'client', 'status', 'tms_or_cat_tool', 'created_date', 'requested_due_date',
                    'last_updated')
    resource_class = RequestResource
admin.site.register(models.Request, RequestAdmin)
