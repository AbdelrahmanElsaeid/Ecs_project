from django.urls import re_path

from src.userswitcher import views

app_name = 'userswitcher'


urlpatterns = [
    re_path(r'^switch/$', views.switch, name='switch'),
]




