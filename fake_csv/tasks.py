from pathlib import Path

import pandas as pd
from celery import shared_task
from faker import Faker

from fake_csv.models import CSVData, CSVSchema, Constants, SchemaColumns
from planeks import settings

path = Path(settings.MEDIA_ROOT)


@shared_task
def test(name):
    return CSVSchema.objects.create(name=name, user_id=1)


@shared_task
def generate_csv_file(rows, schema_id, csv_id):
    fake = Faker()
    gen_data = {
        'STRING': fake.word,
        'FULL_NAME': fake.name,
        'INTEGER': fake.pyint,
        'DATE': fake.date,
        'COMPANY': fake.company,
        'JOB_ROLE': fake.job
    }
    sep = {
        'SEMICOLON': ';',
        'COMMA': ',',
    }
    quotechar = {
        'QUOTE': "'",
        'DOUBLE_QUOTE': '"',
    }

    schema = CSVSchema.objects.get(pk=schema_id)
    columns = SchemaColumns.objects.filter(schema=schema).order_by('order').values()
    csv_obj = CSVData.objects.get(id=csv_id)
    data_columns = {c['name']: c['type'] for c in columns}
    for key in data_columns.keys():
        data = []
        for i in range(rows):
            data.append(gen_data[data_columns[key]]())
        data_columns[key] = data

    df = pd.DataFrame(data_columns, columns=list(data_columns))
    df.to_csv(csv_obj.file, index=False, sep=sep[schema.str_sep], quotechar=quotechar[schema.str_char])
    print(df)

    csv_obj.status = Constants.CSVSchemaStatus.READY
    csv_obj.save()
