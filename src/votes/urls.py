from django.urls import re_path
from django.conf import settings

from src.votes import views

app_name='votes'
urlpatterns = [
    re_path(r'^(?P<vote_pk>\d+)/download/$', views.download_vote, name="download_vote"),
    re_path(r'^(?P<vote_pk>\d+)/sign$', views.vote_sign, name="vote_sign"),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^(?P<vote_pk>\d+)/pdf/debug/$', views.vote_pdf_debug,name="vote_pdf_debug"),
    ]

