from django.urls import path

from src.dashboard import views
app_name = 'dashboard'

urlpatterns = (
    path('', views.view_dashboard, name='view_dashboard'),
)