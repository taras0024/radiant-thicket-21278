from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now
from model_utils import Choices


class Constants:
    CSVSchemaStatus = Choices(
        ("READY", "READY"),
        ("PROCESSING", "PROCESSING")
    )
    SchemaColumns = Choices(
        ("STRING", "STRING"),
        ("FULL_NAME", "FULL_NAME"),
        ("INTEGER", "INTEGER"),
        ("DATE", "DATE"),
        ("COMPANY", "COMPANY"),
        ("JOB_ROLE", "JOB_ROLE"),
    )
    StringSeparators = Choices(
        ("SEMICOLON", ";"),
        ("COMMA", ",")
    )
    StringChar = Choices(
        ("QUOTE", "'"),
        ("DOUBLE_QUOTE", '"')
    )


class CSVSchema(models.Model):
    """Schema of csv"""
    name = models.CharField(max_length=255)
    str_sep = models.CharField(
        max_length=16,
        choices=Constants.StringSeparators,
        default=Constants.StringSeparators.COMMA
    )
    str_char = models.CharField(
        max_length=16,
        choices=Constants.StringChar,
        default=Constants.StringChar.DOUBLE_QUOTE
    )
    modified_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Schema"
        verbose_name_plural = "Schemas"


class SchemaColumns(models.Model):
    """Columns of schema"""
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=128,
        choices=Constants.SchemaColumns,
        default=Constants.SchemaColumns.STRING
    )
    range_from = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    range_to = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    order = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    schema = models.ForeignKey(
        to=CSVSchema,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Schema column"
        verbose_name_plural = "Schema columns"


class CSVData(models.Model):
    """Data of csv"""
    created_at = models.DateTimeField(default=now)
    status = models.CharField(
        max_length=128,
        blank=False,
        choices=Constants.CSVSchemaStatus,
        default=Constants.CSVSchemaStatus.PROCESSING,
    )
    file_name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    schema = models.ForeignKey(to=CSVSchema, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file_name)

    class Meta:
        verbose_name = "CSV Data"
