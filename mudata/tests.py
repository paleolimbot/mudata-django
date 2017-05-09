
import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Dataset, Location, Param, Column, Datum, DatumRaw
from .datetime_parse import datetime_parse


class TagsFieldTests(TestCase):

    def test_tag_field_validation(self):
        # valid dataset with default tags
        ds_valid = Dataset(dataset='a_valid_slug')
        # make sure clean/save works
        ds_valid.full_clean()
        ds_valid.save()

        # valid dataset with dict tags
        ds_valid = Dataset(dataset='a_valid_slug_2', tags={'key': 'value'})
        # make sure clean/save works
        ds_valid.full_clean()
        ds_valid.save()

        # valid dataset with json string tags
        ds_valid = Dataset(dataset='a_valid_slug_3', tags='{"key": "value"}')
        # make sure clean/save works
        ds_valid.full_clean()
        ds_valid.save()

        # invalid tags
        ds_invalid_tags = Dataset(dataset='dataset', tags='[not&json_string}')  # invalid string
        self.assertRaises(ValidationError, ds_invalid_tags.full_clean)
        ds_invalid_tags = Dataset(dataset='dataset', tags=str)  # wrong type
        self.assertRaises(ValidationError, ds_invalid_tags.full_clean)
        ds_invalid_tags = Dataset(dataset='dataset', tags=str)  # wrong type, but currently only raises error on save
        self.assertRaises(ValidationError, ds_invalid_tags.save)


class DatasetModelTests(TestCase):

    def test_dataset_validation(self):
        """
        Test that dataset validation works properly
        """
        # valid dataset
        ds_valid = Dataset(dataset='a_valid_slug')
        # will raise ValidationError if invalid
        ds_valid.full_clean()
        ds_valid.save()

        # unique dataset slugs
        ds_not_unique = Dataset(dataset='a_valid_slug')
        self.assertRaises(ValidationError, ds_not_unique.full_clean)

        # invalid slug
        ds_invalid_slug = Dataset(dataset='not a valid slug')
        self.assertRaises(ValidationError, ds_invalid_slug.full_clean)

        # invalid tags
        ds_invalid_tags = Dataset(dataset='dataset', tags='[not&json_string}')
        self.assertRaises(ValidationError, ds_invalid_tags.full_clean)


class LocationModelTests(TestCase):

    def test_location_validation(self):
        """
        Test that location validation works properly
        """
        # create dataset
        ds = Dataset(dataset='dataset')
        ds.save()

        # valid location
        loc_valid = Location(dataset=ds, location='location')
        # should raise validation error if bad
        loc_valid.full_clean()
        loc_valid.save()

        # non-unique location
        loc_duplicate = Location(dataset=ds, location='location')
        self.assertRaises(ValidationError, loc_duplicate.full_clean)

        # invalid dataset
        loc_invalid = Location(dataset=None, location='location2')
        self.assertRaises(ValidationError, loc_invalid.full_clean)
        # invalid slug
        loc_invalid = Location(dataset=ds, location='location bad slug')
        self.assertRaises(ValidationError, loc_invalid.full_clean)
        # invalid tags
        loc_invalid = Location(dataset=ds, location='location3', tags='&not_json]')
        self.assertRaises(ValidationError, loc_invalid.full_clean)


class ParamModelTests(TestCase):

    def test_param_validation(self):
        """
        Tests param validation methods
        """
        # create dataset
        ds = Dataset(dataset='dataset')
        ds.save()

        # valid param
        param_valid = Param(dataset=ds, param='param')
        # should raise validation error if bad
        param_valid.full_clean()
        param_valid.save()

        # duplicate param
        param_duplicate = Param(dataset=ds, param='param')
        self.assertRaises(ValidationError, param_duplicate.full_clean)

        # invalid dataset
        param_invalid = Param(dataset=None, param='param2')
        self.assertRaises(ValidationError, param_invalid.full_clean)
        # invalid slug
        param_invalid = Param(dataset=ds, param='param bad slug')
        self.assertRaises(ValidationError, param_invalid.full_clean)
        # invalid tags
        param_invalid = Param(dataset=ds, param='param3', tags='&not_json]')
        self.assertRaises(ValidationError, param_invalid.full_clean)


class ColumnModelTests(TestCase):

    def test_column_validation(self):
        """
        Column model validation tests
        """
        # create dataset
        ds = Dataset(dataset='dataset')
        ds.save()

        # create column
        valid_col = Column(dataset=ds, table='data', column='x')
        valid_col.full_clean()
        valid_col.save()

        # duplicate column
        dup_col = Column(dataset=ds, table='data', column='x')
        self.assertRaises(ValidationError, dup_col.full_clean)

        # invalid dataset
        bad_col = Column(dataset=None, table='data', column='x')
        self.assertRaises(ValidationError, bad_col.full_clean)

        # invalid table
        bad_col = Column(dataset=ds, table='not a table', column='x')
        self.assertRaises(ValidationError, bad_col.full_clean)

        # invalid column
        bad_col = Column(dataset=ds, table='locations', column=None)
        self.assertRaises(ValidationError, bad_col.full_clean)

        # bad tags
        bad_col = Column(dataset=ds, table='locations', column='location', tags='[&not json}')
        self.assertRaises(ValidationError, bad_col.full_clean)


class DateTimeConversionTests(TestCase):

    def test_datetime_autoconvert(self):
        # None should be None
        self.assertIsNone(datetime_parse(None))

        # try all the valid types
        date_strings = ['2017-05-09', '2017-05-09 17:25', '2017-05-09 17:25 -0300',
                        '2017-05-09 17:25:48', '2017-05-09 17:25:48 -0300']

        # check dates
        for date_string in date_strings:
            dt = datetime_parse(date_string)
            self.assertEqual(dt.year, 2017)
            self.assertEqual(dt.month, 5)
            self.assertEqual(dt.day, 9)

        # check times
        for date_string in date_strings[1:3]:
            dt = datetime_parse(date_string)
            self.assertEqual(dt.hour, 17)
            self.assertEqual(dt.minute, 25)

        # check seconds
        for date_string in date_strings[3:5]:
            dt = datetime_parse(date_string)
            self.assertEqual(dt.second, 48)

        # check time zones
        for date_string in [date_strings[2], date_strings[4]]:
            dt = datetime_parse(date_string)
            self.assertIsNotNone(dt.tzinfo)


class DataModelTests(TestCase):

    def test_data_validation(self):
        # create dataset
        ds = Dataset(dataset='dataset')
        ds.save()

        # valid location
        loc = Location(dataset=ds, location='location')
        loc.save()

        # valid param
        param = Param(dataset=ds, param='param')
        param.save()

        def now():
            return datetime.datetime.now(tz=datetime.timezone.utc)

        t1 = now()

        # valid datum (utc to avoid warnings)
        valid_datum = Datum(dataset=ds, location=loc, param=param, x=t1, value='a value')
        valid_datum.full_clean()
        valid_datum.save()

        # blank value should be ok
        valid_datum_2 = Datum(dataset=ds, location=loc, param=param, x=now(), value=None)
        valid_datum_2.full_clean()
        valid_datum_2.save()

        # duplicate datum
        dup_datum = Datum(dataset=ds, location=loc, param=param, x=t1, value='another value')
        self.assertRaises(ValidationError, dup_datum.full_clean)

        # bad dataset
        bad_datum = Datum(dataset=None, location=loc, param=param, x=now())
        self.assertRaises(ValidationError, bad_datum.full_clean)

        # bad location
        bad_datum = Datum(dataset=ds, location=None, param=param, x=now())
        self.assertRaises(ValidationError, bad_datum.full_clean)

        # bad param
        bad_datum = Datum(dataset=ds, location=loc, param=None, x=now())
        self.assertRaises(ValidationError, bad_datum.full_clean)

        # bad x
        bad_datum = Datum(dataset=ds, location=loc, param=param, x=None)
        self.assertRaises(ValidationError, bad_datum.full_clean)

        # bad tags
        bad_datum = Datum(dataset=ds, location=loc, param=param, x=now(), tags='{notjson]*')
        self.assertRaises(ValidationError, bad_datum.full_clean)
