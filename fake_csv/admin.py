from django.contrib import admin

from fake_csv.models import CSVData, CSVSchema, SchemaColumns


class SchemaColumnsInLineAdmin(admin.TabularInline):
    model = SchemaColumns


@admin.register(CSVSchema)
class CSVSchemaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'modified_at')
    search_fields = ('id', 'name',)
    inlines = [SchemaColumnsInLineAdmin, ]


@admin.register(CSVData)
class CSVDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status')
