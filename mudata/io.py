
import zipfile
import tempfile
import os
import csv
import contextlib
from django.core.exceptions import ObjectDoesNotExist

from .datetime_parse import datetime_parse
from .models import Dataset, Location, Param, Column, DatumRaw, Datum


@contextlib.contextmanager
def import_context():
    try:
        yield
    except Exception as e:
        # if an exception was raised, undo the addition of objects
        raise e


def missing_columns(header_line, required_columns):
    return [col_name for col_name in required_columns if col_name not in header_line]


def import_mudata(zip_file):
    """
    Import a mudata zipfile
    :param zip_file: 
    :param update: 
    :return: 
    """

    # keep track of database additions so that they can be undone if import does not
    # complete
    new_objects = []

    # create a tempfile, open the zip file, use import_context to cleanup objects if something goes wrong
    with import_context(), tempfile.TemporaryDirectory() as tmp_dir, zipfile.ZipFile(zip_file, 'r') as zip_ref:

        # extract the zip_file to the temporary directory
        zip_ref.extractall(tmp_dir)

        # find files
        fnames = {}
        for fname in ('datasets.csv', 'locations.csv', 'params.csv', 'columns.csv', 'data.csv'):
            for root, dir, filenames in os.walk(tmp_dir):
                if fname in filenames:
                    fnames[fname] = os.path.join(root, fname)
                    break

        # iterate through datasets
        if 'datasets.csv' not in fnames:
            raise ValueError('"datasets.csv" not found in import file')

        # datasets keeps reference to datasets by name for quick lookup/cleanup later
        datasets = {}
        with open(fnames['datasets.csv'], 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            missing_cols = missing_columns(header, ('dataset', 'tags'))
            if missing_cols:
                raise ValueError('"dataset.csv" is missing column(s): ' + ', '.join(missing_cols))
            for line_number, line in enumerate(reader):
                # check number of columns on each line
                if len(line) == 0:
                    continue
                elif len(line) != 2:
                    raise ValueError('Wrong number of columns in "dataset.csv" on line %s' % (line_number + 2))

                # create dataset object
                ds = Dataset(dataset=line[0], tags=line[1])

                # check for existing dataset, make sure tags match
                try:
                    ds = Dataset.objects.get(dataset=ds.dataset)
                except ObjectDoesNotExist:
                    # validate dataset object
                    ds.full_clean()
                    # add to database
                    ds.save()
                    new_objects.append(ds)

                # keep reference to the (now saved in db) dataset
                datasets[line[0]] = ds

        # iterate through locations
        if 'locations.csv' not in fnames:
            raise ValueError('"locations.csv" not found in import file')

        locations = {}
        with open(fnames['locations.csv'], 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            missing_cols = missing_columns(header, ('dataset', 'location', 'tags'))
            if missing_cols:
                raise ValueError('"location.csv" is missing column(s): ' + ', '.join(missing_cols))
            for line_number, line in enumerate(reader):
                # check columns on each line
                if len(line) == 0:
                    continue
                elif len(line) != 3:
                    raise ValueError('Wrong number of columns in "locations.csv" on line %s' % (line_number + 2))

                # find dataset object
                ds = datasets[line[0]]
                # create location object
                loc = Location(dataset=ds, location=line[1], tags=line[2])

                # check for existing location, make sure tags match
                try:
                    loc = Location.objects.get(dataset=ds, location=loc.location)
                except ObjectDoesNotExist:
                    # validate location object
                    loc.full_clean()
                    # add to database
                    loc.save()
                    new_objects.append(loc)

                # keep reference to the (saved in db) location
                locations[line[0]+line[1]] = loc

        # iterate through parameters
        if 'params.csv' not in fnames:
            raise ValueError('"params.csv" not found in import file')

        params = {}
        with open(fnames['params.csv'], 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            missing_cols = missing_columns(header, ('dataset', 'param', 'tags'))
            if missing_cols:
                raise ValueError('"params.csv" is missing column(s): ' + ', '.join(missing_cols))
            for line_number, line in enumerate(reader):
                # check columns on each line
                if len(line) == 0:
                    continue
                elif len(line) != 3:
                    raise ValueError('Wrong number of columns in "params.csv" on line %s' % (line_number + 2))

                # find dataset object
                ds = datasets[line[0]]
                # create param object
                param = Param(dataset=ds, param=line[1], tags=line[2])

                # check for existing param, make sure tags match
                try:
                    param = Param.objects.get(dataset=ds, param=param.param)
                except ObjectDoesNotExist:
                    # validate param object
                    param.full_clean()
                    # add to database
                    param.save()

                # keep reference to the (saved in db) location
                params[line[0] + line[1]] = param

        # iterate through columns
        if 'columns.csv' not in fnames:
            raise ValueError('"columns.csv" not found in import file')

        with open(fnames['columns.csv'], 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            missing_cols = missing_columns(header, ('dataset', 'table', 'column', 'tags'))
            if missing_cols:
                raise ValueError('"columns.csv" is missing column(s): ' + ', '.join(missing_cols))
            for line_number, line in enumerate(reader):
                # check columns on each line
                if len(line) == 0:
                    continue
                elif len(line) != 4:
                    raise ValueError('Wrong number of columns in "columns.csv" on line %s' % (line_number + 2))

                # find dataset object
                ds = datasets[line[0]]
                # create column object
                column = Column(dataset=ds, table=line[1], column=line[2], tags=line[3])

                # check for existing column entry before adding
                try:
                    Column.objects.get(dataset=ds, table=column.table, column=column.column)
                except ObjectDoesNotExist:
                    # validate param object
                    column.full_clean()
                    # add to database
                    column.save()

        # iterate through data
        if 'data.csv' not in fnames:
            raise ValueError('"data.csv" not found in import file')

        with open(fnames['data.csv'], 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            missing_cols = missing_columns(header, ('dataset', 'location', 'param', 'x', 'value', 'tags'))
            if missing_cols:
                raise ValueError('"data.csv" is missing column(s): ' + ', '.join(missing_cols))
            for line_number, line in enumerate(reader):
                # check columns on each line
                if len(line) == 0:
                    continue
                elif len(line) != 6:
                    raise ValueError('Wrong number of columns in "data.csv" on line %s' % (line_number + 2))

                # find dataset object
                ds = datasets[line[0]]
                # find location object
                location = locations[line[0]+line[1]]
                # find param object
                param = params[line[0]+line[2]]

                # make sure NA values are None
                value = None if line[4] in ('', 'NA') else line[4]

                # parse x value
                try:
                    x = datetime_parse(line[3])
                    datum = Datum(dataset=ds, location=location, param=param, x=x, value=value, tags=line[5])
                except ValueError:
                    datum = DatumRaw(dataset=ds, location=location, param=param, x=line[3], value=value, tags=line[5])

                # check for existing datum, but this time fail if there is an attempt to add duplicate data
                # this should fail on full_clean
                datum.full_clean()
                # add to database
                datum.save()

