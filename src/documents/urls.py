from django.urls import path, re_path

from src.documents import views
app_name = 'documents'
urlpatterns = [
    re_path(r'^ref/(?P<ref_key>[0-9a-f]{32})/$', views.download_once,name='download_once'),
]