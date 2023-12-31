import sys

from django.urls import path,re_path

from src.signature import views
app_name='signature'


urlpatterns = [
    re_path(r'^batch/(?P<sign_session_id>\d+)/$', views.batch_sign, name='batch_sign'),
    re_path(r'^send/(?P<pdf_id>\d+)/$', views.sign_send, name='sign_send'),
    re_path(r'^error/(?P<pdf_id>\d+)/$', views.sign_error, name='sign_error'),
    re_path(r'^preview/(?P<pdf_id>\d+)/$', views.sign_preview, name='sign_preview'),
    re_path(r'^action/(?P<pdf_id>\d+)/(?P<action>[^/]+)/$', views.batch_action, name='batch_action'),
    re_path(r'^receive/(?P<pdf_id>\d+)/$', views.sign_receive, name='sign_receive'),
]

if 'test' in sys.argv:
    from src.signature.tests import sign_success, sign_fail
    urlpatterns += [
        re_path(r'^test/success/$', sign_success, name='sign_success'),
        re_path(r'^test/failure/$', sign_fail, name='sign_fail'),
    ]



