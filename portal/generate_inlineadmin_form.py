# http://www.alexanderinteractive.com/blog/2012/09/generating-an-inlineadmin-form-on-the-fly-in-django/
from django.template import loader, Context
from django.contrib.admin import helpers
from django.contrib import admin
from .models import Scoping


def get_inline_form(request, parent_object, scoping_admin, pricing_inline):
    formset = None
    inline = None
    scoping_id = parent_object.id
    scoping = Scoping.objects.get(id=scoping_id)
    # get the current site
    admin_site = admin.site
    scoping_admin_instance = scoping_admin(Scoping, admin_site)

    # get all possible inlines for the parent Admin
    inline_instances = scoping_admin_instance.get_inline_instances(request)
    prefixes = {}

    for FormSet, inline in zip(scoping_admin_instance.get_formsets_with_inlines(request, scoping), inline_instances):
        # get the inline of interest and generate it's formset
        if isinstance(inline, pricing_inline):
            prefix = FormSet[0].get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet[0](instance=scoping, prefix=prefix)

    # get possible fieldsets, readonly, and prepopulated information for the parent Admin
    fieldsets = list(inline.get_fieldsets(request, scoping))
    readonly = list(inline.get_readonly_fields(request, scoping))
    prepopulated = dict(inline.get_prepopulated_fields(request, scoping))

    # generate the inline formset
    inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets, prepopulated, readonly,
                                                      model_admin=scoping_admin_instance)

    # render the template
    t = loader.get_template('admin/edit_inline/tabular.html')
    c = Context({'inline_admin_formset': inline_admin_formset})
    rendered_inline_form = t.render(c)
    return rendered_inline_form
