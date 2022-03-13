from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.forms.models import inlineformset_factory

from fake_csv.models import CSVSchema, SchemaColumns


class CSVSchemaForm(forms.ModelForm):
    class Meta:
        model = CSVSchema
        fields = ('name', 'str_sep', 'str_char')


class SchemaColumnsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.schema_id = kwargs.pop('schema_id', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = SchemaColumns
        fields = ('name', 'type', 'order')

    def clean(self):
        cleaned_data = super().clean()
        if self.schema_id:
            obj = SchemaColumns.objects.filter(schema_id=self.schema_id).order_by('-order').first()
            if obj:
                if not self.instance.id and cleaned_data['order'] != obj.order + 1:
                    raise ValidationError('Wrong ordering')
                if self.instance.id and cleaned_data['order'] != obj.order + 1 and cleaned_data['order'] != self.instance.order:
                    raise ValidationError('Wrong ordering')
            else:
                if cleaned_data['order'] != 0:
                    raise ValidationError('Ordering should start from "0"')
        return cleaned_data


SchemaColumnsFormSet = inlineformset_factory(
    parent_model=CSVSchema,
    model=SchemaColumns,
    form=SchemaColumnsForm,
    can_delete=True,
    min_num=1,
    extra=0
)


class NumRowsForm(forms.Form):
    num_rows = forms.IntegerField(label='Rows', validators=[MinValueValidator(0)])
