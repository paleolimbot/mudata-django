
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .datetime_parse import datetime_parse_numeric
from .models import Dataset, Location, Param, Datum


def index(request):
    return render(request, 'mudata/index.html')


def view_dataset(request, dataset_slug):
    dataset = get_object_or_404(Dataset, dataset=dataset_slug)
    return render(request, 'mudata/view_dataset.html', {'dataset': dataset})


def view_location(request, dataset_slug, location_slug):
    dataset = get_object_or_404(Dataset, dataset=dataset_slug)
    location = get_object_or_404(Location, dataset=dataset.id, location=location_slug)
    return render(request, 'mudata/view_location.html', {'location': location})


def view_param(request, dataset_slug, param_slug):
    dataset = get_object_or_404(Dataset, dataset=dataset_slug)
    param = get_object_or_404(Param, dataset=dataset.id, param=param_slug)
    return render(request, 'mudata/view_param.html', {'param': param})


def query(request, format):

    query_params = request.GET
    # TODO: validate query params (make sure datetime XOR x query is used, not both)

    # extract dataset/location/param restrictions
    datasets = query_params['datasets'].split(' ') if 'datasets' in query_params else []
    locations = query_params['locations'].split(' ') if 'locations' in query_params else []
    params = query_params['params'].split(' ') if 'params' in query_params else []

    # extract 'x' query, parse to float
    try:
        x_from = float(query_params['x_from']) if 'x_from' in query_params else None
    except ValueError:
        raise ValueError("Unparsable x_from: %s" % query_params['x_from'])
    try:
        x_to = float(query_params['x_to']) if 'x_to' in query_params else None
    except ValueError:
        raise ValueError("Unparsable x_to: %s" % query_params['x_to'])

    # extract 'datetime' query
    datetime_from = query_params['datetime_from'] if 'datetime_from' in query_params else None
    datetime_to = query_params['datetime_to'] if 'datetime_to' in query_params else None

    # parse datetime from and to
    if datetime_from is not None:
        if x_from is not None:
            raise RuntimeError("x_from and datetime_from cannot both be passed")
        try:
            x_from = datetime_parse_numeric(datetime_from)
        except ValueError:
            raise ValueError("Unparsable datetime_from: %s" % datetime_from)
    if datetime_to is not None:
        if x_to is not None:
            raise RuntimeError("x_to and datetime_to cannot both be passed")
        try:
            x_to = datetime_parse_numeric(datetime_to)
        except ValueError:
            raise ValueError("Unparsable datetime_to: %s" % datetime_to)

    query_set = Datum.objects.all()
    if datasets:
        dataset_ids = []
        for dataset in datasets:
            dataset_ids.append(get_object_or_404(Dataset, dataset=dataset))
        query_set = query_set.filter(dataset__in=dataset_ids)

    if locations:
        for location_slug in locations:
            location_qs = Location.objects.filter(location=location_slug)
            query_set = query_set.filter(location__in=location_qs)

    if params:
        for param_slug in params:
            param_qs = Param.objects.filter(param=param_slug)
            query_set = query_set.filter(param__in=param_qs)

    if x_from:
        query_set = query_set.filter(x__gte=x_from)
    if x_to:
        query_set = query_set.filter(x__lte=x_to)

    return render(request, 'mudata/query.html',
                    {'result': query_set}
                  )


def plot(request, table, query_string):
    pass
