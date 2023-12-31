
from django.urls import path, re_path

from src.users import views
app_name = 'users'
urlpatterns = [
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('accounts/register/', views.register, name='register'),

    re_path(r'^activate/(?P<token>.+)$', views.activate, name='activate'),
    path('profile/', views.profile, name="profile"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('request-password-reset/', views.request_password_reset, name='request_password_reset'),
    re_path(r'^password-reset/(?P<token>.+)$', views.do_password_reset, name="do_password_reset"),
    re_path(r'^users/(?P<user_pk>\d+)/indisposition/$', views.indisposition, name='indisposition'),
    path('users/notify_return/', views.notify_return, name='notify_return'),
    re_path(r'^users/(?P<user_pk>\d+)/toggle_active/$', views.toggle_active, name='toggle_active'),
    re_path(r'^users/(?P<user_pk>\d+)/details/', views.details, name='details'),
    path('users/administration/', views.administration, name='administration'),
    path('users/invite/', views.invite, name='invite'),
    path('users/login_history/', views.login_history, name='login_history'),
    re_path(r'^accept_invitation/(?P<invitation_uuid>[\da-zA-Z]{32})/$', views.accept_invitation,name='accept_invitation'),
]
