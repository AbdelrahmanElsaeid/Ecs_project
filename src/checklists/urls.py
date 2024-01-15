
from django.urls import re_path
from django.conf import settings
from src.checklists import views

app_name='checklists'
urlpatterns = [
    re_path(r'^(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', views.checklist_comments, name='checklist_comments'),
    re_path(r'^(?P<checklist_pk>\d+)/pdf/$', views.checklist_pdf, name='checklist_pdf'),
    re_path(r'^create_task/submission/(?P<submission_pk>\d+)/$', views.create_task, name='create_task'),
    re_path(r'^categorization_tasks/submissions/(?P<submission_pk>\d+)/$', views.categorization_tasks, name='categorization_tasks'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^(?P<checklist_pk>\d+)/pdf/debug/$', views.checklist_pdf_debug, name='checklist_pdf_debug'),
    ]


