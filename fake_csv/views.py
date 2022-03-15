import datetime
import os
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, FormView, TemplateView, UpdateView

from fake_csv.forms import CSVSchemaForm, NumRowsForm, SchemaColumnsForm
from fake_csv.models import CSVData, CSVSchema, SchemaColumns
from fake_csv.tasks import generate_csv_file
from planeks import settings

MEDIA_PATH = Path(settings.MEDIA_ROOT)


@method_decorator(login_required, name='dispatch')
class CreateCSVSchemasFormView(FormView):
    template_name = 'fake_csv/schema_create.html'
    form_class = CSVSchemaForm
    success_url = '/'

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, 'Created')
        return super().get_success_url()

    def form_valid(self, form):
        data = {
            'name': form.cleaned_data.get('name'),
            'str_sep': form.cleaned_data.get('str_sep'),
            'str_char': form.cleaned_data.get('str_char'),
        }
        CSVSchema.objects.create(**data)
        return super().form_valid(form)


class CSVSchemasView(TemplateView):
    template_name = 'fake_csv/schema_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csvschema_list'] = CSVSchema.objects.all()
        return context


@method_decorator(login_required, name='dispatch')
class CSVSchemasUpdateView(UpdateView):
    model = CSVSchema
    template_name = 'fake_csv/schema_update.html'
    fields = ['name', 'str_sep', 'str_char']
    success_url = reverse_lazy('home')


@method_decorator(login_required, name='dispatch')
class CSVSchemasDeleteView(DeleteView):
    model = CSVSchema
    template_name = 'fake_csv/schema_confirm_delete.html'
    success_url = reverse_lazy('home')


@login_required
def create_schema_columns(request, pk):
    schema = CSVSchema.objects.get(pk=pk)
    form = SchemaColumnsForm(request.POST or None, schema_id=pk)
    columns = SchemaColumns.objects.filter(schema=schema)

    if request.method == 'POST':
        if form.is_valid():
            column = form.save(commit=False)
            column.schema = schema
            column.save()
            return redirect('schema-columns-detail', pk=column.pk)
        else:
            context = {
                'form': form,
            }
            return render(request, 'partials/schema_columns_form.html', context)

    context = {
        'form': form,
        'schema': schema,
        'columns': columns,
    }
    return render(request, 'fake_csv/create_schema_columns.html', context)


@login_required
def create_schema_columns_form(request):
    context = {
        'form': SchemaColumnsForm()
    }
    return render(request, 'partials/schema_columns_form.html', context)


@login_required
def detail_schema_columns(request, pk):
    column = SchemaColumns.objects.get(pk=pk)
    context = {
        'column': column
    }
    return render(request, 'partials/schema_column_detail.html', context)


@login_required
def update_schema_columns(request, pk):
    column = SchemaColumns.objects.get(pk=pk)
    form = SchemaColumnsForm(request.POST or None, instance=column, schema_id=column.schema_id)
    if request.method == 'POST':
        if form.is_valid():
            column = form.save()
            return redirect('schema-columns-detail', pk=column.pk)

    context = {
        'form': form,
        'column': column
    }
    return render(request, 'partials/schema_columns_form.html', context)


@login_required
def delete_schema_columns(request, pk):
    column = SchemaColumns.objects.get(pk=pk)
    column.delete()
    return HttpResponse('')


@login_required
def generate_csv(request, pk):
    schema = CSVSchema.objects.get(pk=pk)
    form = NumRowsForm(request.POST or None)
    csv_data = CSVData.objects.filter(schema=schema)

    if request.method == 'POST':
        if form.is_valid():
            rows = form.cleaned_data['num_rows']
            schema = CSVSchema.objects.get(pk=schema.id)
            file_name = f"{schema.name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
            csv_data = CSVData.objects.create(file_name=file_name, schema_id=schema.id, user_id=request.user.id)
            generate_csv_file.delay(rows, schema.id, csv_data.id)
            return redirect('schema-data-sets', pk=schema.id)
    context = {
        'form': form,
        'csv_data': csv_data,
    }
    return render(request, 'fake_csv/generate_csv.html', context)


@login_required
def upload_file(request, pk):
    file_name = CSVData.objects.get(pk=pk).file_name
    path = (os.path.join(MEDIA_PATH, file_name))
    try:
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    except Exception as e:
        return HttpResponse('Document not found')
