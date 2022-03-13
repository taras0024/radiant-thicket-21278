from django.urls import path
from . import views


urlpatterns = [
    path("schema/create/", views.CreateCSVSchemasFormView.as_view(), name='create-schema'),
    path("", views.CSVSchemasView.as_view(), name='home'),
    path("schema/update/<int:pk>/", views.CSVSchemasUpdateView.as_view(), name='update-schema'),
    path("schema/delete/<int:pk>/", views.CSVSchemasDeleteView.as_view(), name='delete-schema'),

    path("<int:pk>/", views.create_schema_columns, name='create-schema-columns'),
    path("htmx/schema-columns-form/", views.create_schema_columns_form, name='schema-columns-form'),
    path("htmx/schema-columns/<int:pk>/", views.detail_schema_columns, name='schema-columns-detail'),
    path("htmx/schema-columns/update/<int:pk>/", views.update_schema_columns, name='schema-columns-update'),
    path("htmx/schema-columns/delete/<int:pk>/", views.delete_schema_columns, name='schema-columns-delete'),

    path("schema/<int:pk>/data-sets/", views.generate_csv, name='schema-data-sets'),
    path("data-sets/<int:pk>/upload", views.upload_file, name='upload-file'),
]
