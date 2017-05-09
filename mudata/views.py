
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .datetime_parse import datetime_parse
from .models import Dataset, Location, Param, Datum, DatumRaw


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


def query(request, table, format):

    query_params = request.GET
    # TODO: validate query params

    # extract dataset/location/param restrictions
    datasets = query_params['datasets'].split(' ') if 'datasets' in query_params else []
    locations = query_params['locations'].split(' ') if 'locations' in query_params else []
    params = query_params['params'].split(' ') if 'params' in query_params else []

    # extract 'x' query
    x_from = query_params['x_from'] if 'x_from' in query_params else None
    x_to = query_params['x_to'] if 'x_to' in query_params else None

    # choose object_class and x type based on table name
    if table == 'data':
        object_class = Datum
        x_from = datetime_parse(x_from)
        x_to = datetime_parse(x_to)
    elif table == 'raw_data':
        object_class = DatumRaw
    else:
        raise Http404('Table %s does not exist' % table)

    query_set = object_class.objects.all()
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
