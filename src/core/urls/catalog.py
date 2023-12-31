from django.urls import path

from src.core.views import submissions as views


urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('<int:year>/', views.catalog, name='catalog_year'),
    path('json/', views.catalog_json),
]