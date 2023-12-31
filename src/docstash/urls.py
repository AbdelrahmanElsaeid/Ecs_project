from django.urls import path, re_path

from src.docstash import views



urlpatterns = [
    re_path(r'^(?P<docstash_key>.+)/doc/(?P<document_pk>\d+)/$', views.download_document, name='download_document'),
    re_path(r'^(?P<docstash_key>.+)/doc/(?P<document_pk>\d+)/view/$', views.view_document, name='view_document'),
]
