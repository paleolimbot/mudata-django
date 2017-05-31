
from datetime import datetime

EPOCH = datetime(1970, 1, 1, 0, 0, tzinfo=datetime.utcnow().tzinfo)


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


def datetime_numeric(dt):
    return dt.timestamp()


def datetime_parse_numeric(x):
    dt = datetime_parse(x)
    if dt is None:
        return None
    else:
        return datetime_numeric(dt)


def numeric_to_datetime(x):
    datetime.fromtimestamp(x)
