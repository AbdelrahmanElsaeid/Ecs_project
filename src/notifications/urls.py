from django.urls import path, re_path
from src.notifications import views
from django.conf import settings
app_name='notifications'



urlpatterns = [
    re_path(r'^new/$', views.select_notification_creation_type, name='select_notification_creation_type'),
    re_path(r'^new/(?P<notification_type_pk>\d+)/diff/(?P<submission_form_pk>\d+)/$', views.create_diff_notification, name='create_diff_notification'),
    re_path(r'^new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', views.create_notification, name='create_notification'),
    re_path(r'^delete/(?P<docstash_key>.+)/$', views.delete_docstash_entry, name='delete_docstash_entry'),
    re_path(r'^doc/upload/(?P<docstash_key>.+)/$', views.upload_document_for_notification, name='upload_document_for_notification'),
    re_path(r'^doc/delete/(?P<docstash_key>.+)/$', views.delete_document_from_notification, name='delete_document_from_notification'),
    re_path(r'^submission_data_for_notification/$', views.submission_data_for_notification, name='submission_data_for_notification'),
    re_path(r'^investigators_for_notification/$', views.investigators_for_notification, name='investigators_for_notification'),
    re_path(r'^(?P<notification_pk>\d+)/$', views.view_notification, name='view_notification'),
    re_path(r'^(?P<notification_pk>\d+)/pdf/$', views.notification_pdf, name='notification_pdf'),
    re_path(r'^(?P<notification_pk>\d+)/doc/(?P<document_pk>\d+)/$', views.download_document, name='download_document'),
    re_path(r'^(?P<notification_pk>\d+)/doc/(?P<document_pk>\d+)/view/$', views.view_document, name='view_document'),
    re_path(r'^(?P<notification_pk>\d+)/answer/pdf/$', views.notification_answer_pdf, name='notification_answer_pdf'),
    re_path(r'^(?P<notification_pk>\d+)/answer/edit/$', views.edit_notification_answer, name='edit_notification_answer'),
    re_path(r'^(?P<notification_pk>\d+)/answer/sign/$', views.notification_answer_sign, name='notification_answer_sign'),
    re_path(r'^list/open/$', views.open_notifications, name='open_notifications'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^(?P<notification_pk>\d+)/pdf/debug/$', views.notification_pdf_debug, name='notification_pdf_debug'),
        re_path(r'^(?P<notification_pk>\d+)/answer/pdf/debug/$', views.notification_answer_pdf_debug, name='notification_answer_pdf_debug'),
    ]

