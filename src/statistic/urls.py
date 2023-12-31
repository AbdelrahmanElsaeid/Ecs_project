
from django.urls import path, re_path

from src.statistic import views
app_name='statistic'
urlpatterns = [
    
    re_path(r'^(?:(?P<year>\d{4})/)?$', views.stats, name='stats'),
]




