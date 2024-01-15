from django.urls import path, re_path
from src.core.views import comments as views

# urlpatterns = [
#     path('submission/<int:submission_pk>/', views.index, name='index'),
#     path('submission/<int:submission_pk>/new/', views.edit, name='edit'),
#     path('<int:pk>/edit/', views.edit),
#     path('<int:pk>/delete/', views.delete),
#     path('<int:pk>/attachment/', views.download_attachment),
#     path('<int:pk>/attachment/view/', views.view_attachment),
# ]

urlpatterns = [
    re_path(r'^submission/(?P<submission_pk>\d+)/$', views.index, name='index'),
    re_path(r'^submission/(?P<submission_pk>\d+)/new/$', views.edit, name='edit'),
    re_path(r'^(?P<pk>\d+)/edit/$', views.edit, name='edit'),
    re_path(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),
    re_path(r'^(?P<pk>\d+)/attachment/$', views.download_attachment, name='download_attachment'),
    re_path(r'^(?P<pk>\d+)/attachment/view/$', views.view_attachment, name='view_attachment'),
]