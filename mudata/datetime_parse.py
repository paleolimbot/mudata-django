
from datetime import datetime


def datetime_parse(x):
    if x is None:
        return x

    for date_format in ('%Y-%m-%d', '%Y-%m-%d %H:%M %z', '%Y-%m-%d %H:%M:%S %z',
                        '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(x, date_format)
        except ValueError:
            pass

    raise ValueError('Could not parse x value: %s' % x)