from django.contrib import admin
from django.forms.widgets import TextInput

from .models import Dataset, Location, Param, Column, Datum, TagsField


class TaggedAdmin(admin.ModelAdmin):
    formfield_overrides = {
        # TODO: really need a key/value widget of some kind
        TagsField: {'widget': TextInput},
    }


class DatumAdmin(TaggedAdmin):
    fields = ('dataset', 'location', 'param', 'x', 'value', 'tags')

admin.site.register(Dataset, TaggedAdmin)
admin.site.register(Location, TaggedAdmin)
admin.site.register(Param, TaggedAdmin)
admin.site.register(Column, TaggedAdmin)
admin.site.register(Datum, DatumAdmin)
