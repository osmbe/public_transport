from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /lines/
    url(r'^$', views.index, name='index'),
    # ex: /lines/5/
    url(r'^(?P<line_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /lines/5/results/
    url(r'^(?P<line_id>[0-9]+)/results/$', views.results, name='results'),
]
