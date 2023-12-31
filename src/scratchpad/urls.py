
from django.urls import re_path

from src.scratchpad import views

app_name = 'scratchpad'



urlpatterns = [
    re_path(r'^popup/(?:(?P<scratchpad_pk>\d+)/)?$', views.popup, name='popup'),
    re_path(r'^popup/list/$', views.popup_list, name='popup_list'),
]
