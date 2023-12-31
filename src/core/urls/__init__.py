from django.urls import path, include, re_path

from src.core.views import logo
from src.core.views.fieldhistory import field_history
from src.core.views.administration import advanced_settings
from src.core.views.autocomplete import autocomplete

app_name = 'core'

urlpatterns = [
    path('logo/', logo, name='logo'),
    path('fieldhistory/<str:model_name>/<int:pk>/', field_history, name="field_history"),
    path('advanced_settings/', advanced_settings, name='advanced_settings'),
    #path('autocomplete/<str:queryset_name>/', autocomplete, name='autocomplete'),
    re_path(r'^autocomplete/(?P<queryset_name>[^/]+)/$', autocomplete, name='autocomplete'),

    path('submission/', include('src.core.urls.submission')),
    path('comments/', include('src.core.urls.comments')),
    path('catalog/', include('src.core.urls.catalog')),
]