
from django.conf.urls import url
from . import views

app_name = 'mudata'
urlpatterns = [
    # the index page
    url(r'^$', views.index),

    # the 'veiw' action
    url(r'^view/dataset/(?P<dataset_slug>[a-zA-Z0-9_-]+)/$',
        views.view_dataset, name='view_dataset'),
    url(r'^view/location/(?P<dataset_slug>[a-zA-Z0-9_-]+)/(?P<location_slug>[a-zA-Z0-9_-]+)/$',
        views.view_location, name='view_location'),
    url(r'^view/param/(?P<dataset_slug>[a-zA-Z0-9_-]+)/(?P<param_slug>[a-zA-Z0-9_-]+)/$',
        views.view_param, name='view_param'),

    # the 'query' action
    url(r'^query/(?P<format>html|json)$', views.query, name='query'),

    # the 'plot' action
    url(r'^plot/(?P<format>html|json)$', views.plot, name='plot'),
]
