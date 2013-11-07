from django.conf.urls import patterns, url
from drinkers.views import DrinkerView

urlpatterns = patterns('',
    url(r'^main', DrinkerView.as_view()),
    # url(r'^sampling', 'web.views.sampling'),
    # url(r'^record', 'web.views.start_sampling'),
    # url(r'^recommendation', 'web.views.recommendation'),
)
