from django.urls import path,re_path

from src.pki import views

app_name= 'pki'



urlpatterns = [
    re_path(r'^pki/certs/new/$', views.create_cert, name='create_cert'),
    re_path(r'^pki/certs/$', views.cert_list, name='cert_list'),
    re_path(r'^pki/certs/(?P<cert_pk>\d+)/revoke/$', views.revoke_cert, name='revoke_cert'),
]


