from django.conf.urls import url

from . import views

app_name = 'cfgRepo'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^dir/(?P<pk>[0-9]+)/$', views.DirectoryView.as_view(), name='dir'),
    url(r'^(?P<pk>[0-9]+)/$', views.SnippetView.as_view(), name='snippet'),
    url(r'^snippetHistory/(?P<pk>[0-9]+)/$', views.SnippetHistoryView.as_view(), name='snippetHistory'),
    url(r'^createSnippetHistory$', views.CreateSnippetHistoryView.as_view(), name='createSnippetHistory'),
    url(r'^updateSnippet$', views.UpdateSnippetView.as_view(), name='updateSnippet'),
    url(r'^createDir$', views.CreateDirectoryView.as_view(), name='createDir'),
]

