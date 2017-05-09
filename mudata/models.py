
import json
from django.db import models


class TaggedModel(models.Model):
    """
    mudata tables all have an arbitrary number of columns, so the non-required
    (i.e. non-queried) columns are stored as JSON in the 'tags' column. These methods
    handle key/value setting/getting for extra columns. Extra columns do not have a 
    meaning for 'missing' values, so None/null/NA/'' values are treated as equivalent.
    """

    def tags_get(self):
        return json.loads(self.tags)

    def tag_set(self, **kwargs):
        dct = json.loads(self.tags)
        for key, value in kwargs.items():
            if key in dct and ((value is None) or (value == '')):
                del dct[key]
            elif value is not None:
                dct[key] = value
        self.tags = json.dumps(dct)
        return dct

    def tag_get(self, tag):
        tags = json.loads(self.tags)
        if tag in tags:
            return tags[tag]
        else:
            return None

    class Meta:
        abstract = True


class Dataset(TaggedModel):
    """
    Datasets are a scope where the meaning of location, param, and column are consistent
    """
    dataset = models.SlugField(unique=True)
    tags = models.TextField(default='{}')

    def __str__(self):
        return self.dataset


class Location(TaggedModel):
    """
    Locations are discrete spatial entities (e.g., climate stations) whose identifier
    carries consistent meaning within a dataset. This table stores information about each
    location.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    location = models.SlugField()
    tags = models.TextField(default='{}')

    def __str__(self):
        return ' / '.join(str(x) for x in (self.dataset, self.location))

    class Meta:
        unique_together = ('dataset', 'location',)


class Param(TaggedModel):
    """
    Params are measured parameters (e.g., temperature). This table stores information
    about each parameter.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    param = models.SlugField()
    tags = models.TextField(default='{}')

    def __str__(self):
        return ' / '.join(str(x) for x in (self.dataset, self.param))

    class Meta:
        unique_together = ('dataset', 'param',)


class Column(TaggedModel):
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
    tags = models.TextField(default='{}')

    def __str__(self):
        return ' / '.join(str(x) for x in (self.dataset, self.table, self.column))

    class Meta:
        unique_together = ('dataset', 'table', 'column',)


class AbstractDatum(TaggedModel):
    """
    This table contains the data. Each datum has a dataset, location, param, and an 'x' value.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    param = models.ForeignKey(Param, on_delete=models.CASCADE)
    value = models.CharField(max_length=200, blank=True, null=True)
    tags = models.TextField(default='{}')

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
