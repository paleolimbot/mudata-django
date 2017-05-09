from django.contrib import admin

from .models import Dataset, Location, Param, Column, Datum, DatumRaw


class DatumInline(admin.TabularInline):
    fields = ('dataset', 'location', 'param', 'x', 'value', 'tags')
    model = Datum
    extra = 0


class DatumRawInline(admin.TabularInline):
    fields = ('dataset', 'location', 'param', 'x', 'value', 'tags')
    model = DatumRaw
    extra = 0


class DatumInlineAdmin(admin.ModelAdmin):
    inlines = [DatumInline, DatumRawInline]


class DatumAdmin(admin.ModelAdmin):
    fields = ('dataset', 'location', 'param', 'x', 'value', 'tags')

admin.site.register(Dataset)
admin.site.register(Location, DatumInlineAdmin)
admin.site.register(Param, DatumInlineAdmin)
admin.site.register(Column)
admin.site.register(Datum, DatumAdmin)
admin.site.register(DatumRaw, DatumAdmin)
