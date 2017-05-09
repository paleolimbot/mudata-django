
import json
from django.db import models
from django import forms
from django.core.exceptions import ValidationError


class TagsField(models.TextField):
    """
    This custom field handles converting data from a dict to a json and back
    """

    def __init__(self, *args, **kwargs):
        kwargs['default'] = '{}'
        kwargs['blank'] = True
        kwargs['null'] = True
        super(TagsField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return {}
        else:
            return json.loads(value)

    def to_python(self, value):
        if value is None:
            return {}
        elif isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError as e:
                raise ValidationError('The value `%(value)s` could not be converted to JSON (%(error)s)',
                                      params={'value': value, 'error': str(e)}, code='invalid')
        else:
            raise ValidationError('Object of type "%(objtype)s" could not be converted to a dict',
                                  params={'objtype': type(value).__name__}, code='invalid')

    def get_prep_value(self, value):
        if value is None:
            return '{}'
        elif isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError('Object of type "%(objtype)s" could not be converted to a dict',
                                  params={'objtype': type(value).__name__}, code='invalid')

    def deconstruct(self):
        name, path, args, kwargs = super(TagsField, self).deconstruct()
        del kwargs['default']
        del kwargs['blank']
        del kwargs['null']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': forms.CharField}
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 200
        defaults.update(kwargs)
        return super(TagsField, self).formfield(**defaults)


class Dataset(models.Model):
    """
    Datasets are a scope where the meaning of location, param, and column are consistent
    """
    dataset = models.SlugField(unique=True)
    tags = TagsField()

    def __str__(self):
        return self.dataset


class Location(models.Model):
    """
    Locations are discrete spatial entities (e.g., climate stations) whose identifier
    carries consistent meaning within a dataset. This table stores information about each
    location.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    location = models.SlugField()
    tags = TagsField()

    def __str__(self):
        return ' / '.join(str(x) for x in (self.dataset, self.location))

    class Meta:
        unique_together = ('dataset', 'location',)


class Param(models.Model):
    """
    Params are measured parameters (e.g., temperature). This table stores information
    about each parameter.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    param = models.SlugField()
    tags = TagsField()

    def __str__(self):
        return ' / '.join(str(x) for x in (self.dataset, self.param))

    class Meta:
        unique_together = ('dataset', 'param',)


class Column(models.Model):
    """
    User-defined tags and some required columns (x and value in the 'data' table, in particular)
    need metadata to display and/or parse the data.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    table = models.CharField(max_length=200, choices=(
        ('datasets', 'datasets'), ('locations', 'locations'), ('params', 'params'),
        ('data', 'data'), ('columns', 'columns')
    ))
    column = models.SlugField()
    tags = TagsField()

    def __str__(self):
        return ' / '.join(str(x) for x in (self.dataset, self.table, self.column))

    class Meta:
        unique_together = ('dataset', 'table', 'column',)


class AbstractDatum(models.Model):
    """
    This table contains the data. Each datum has a dataset, location, param, and an 'x' value.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    param = models.ForeignKey(Param, on_delete=models.CASCADE)
    value = models.CharField(max_length=200, blank=True, null=True)
    tags = TagsField()

    class Meta:
        abstract = True

    def __str__(self):
        return ' / '.join(str(x) for x in [self.dataset.dataset, self.location.location, self.param.param, self.x]) + \
            ' => ' + str(self.value)


class Datum(AbstractDatum):
    """
    Here the 'x' value is a datetime value. The granularity of the 'x' column could be stored
    in the appropriate row in the 'columns' table. The valid datetime range differs by 
    database, but is generally from 1000 AD to 9999 AD. This obviously restricts storing data
    in this table for some long-range paleo studies, but the simplicity of datetime conversion
    is probably worth it. Other values are stored in the DatumRaw table.
    """

    x = models.DateTimeField()

    class Meta:
        verbose_name_plural = "data"
        unique_together = ('dataset', 'location', 'param', 'x', )


class DatumRaw(AbstractDatum):
    """
    This table is identical to Datum except its 'x' values are strings and not
    datetime objects. This table is intended for use with 'x' values that are not
    datetime values. The type and meaning of 'x' should be encoded in the appropriate
    row in the 'columns' table.
    """

    x = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "raw data"
        unique_together = ('dataset', 'location', 'param', 'x',)
