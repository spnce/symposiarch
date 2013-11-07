from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^start', 'web.views.index'),
    url(r'^sampling', 'web.views.sampling'),
    url(r'^record', 'web.views.start_sampling'),
    url(r'^recommendation', 'web.views.recommendation'),
)
