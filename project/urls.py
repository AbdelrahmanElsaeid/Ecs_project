"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path("admin/", admin.site.urls),
# ]



from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve
from django.shortcuts import render
from django.views.generic.base import RedirectView
# from src.core.admin import admin
from django.contrib import admin
from src.utils import forceauth

def handler500(request):
    ''' 500 error handler which includes ``request`` in the context '''
    return render(request, '500.html', status=500)


urlpatterns = [
    # Default redirect is same as redirect from login if no redirect is set (/dashboard/)
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url=settings.LOGIN_REDIRECT_URL, permanent=False)),

    path('', include('src.users.urls', namespace='users')),
    path('core/', include(('src.core.urls','core'), namespace='core')),
    path('docstash/', include('src.docstash.urls')),
    path('checklist/', include(('src.checklists.urls', 'checklists'), namespace='checklists')),
    path('vote/', include('src.votes.urls', namespace='votes')),
    path('dashboard/', include('src.dashboard.urls', namespace='dashboard')),
    path('task/', include('src.tasksv.urls', namespace='tasksv')),
    path('communication/', include('src.communication.urls', namespace='communication')),
    path('billing/', include(('src.billing.urls', 'billing'), namespace='billing')),
    path('boilerplate/', include('src.boilerplate.urls', namespace='boilerplate')),
    path('scratchpad/', include('src.scratchpad.urls', namespace='scratchpad')),
    path('document/', include('src.documents.urls')),
    path('meeting/', include('src.meetings.urls', namespace='meetings')),
    path('notification/', include('src.notifications.urls', namespace='notifications')),
    path('signature/', include('src.signature.urls', namespace='signature')),
    path('statistics/', include('src.statistic.urls', namespace='statistic')),
    path('tags/', include('src.tags.urls', namespace='tags')),
    path('', include(('src.pki.urls', 'pki'), namespace='pki')),
    # path('', include('src.pki.urls', namespace='pki')),
    path('i18n/', include('django.conf.urls.i18n')),
    re_path(r'^static/(?P<path>.*)$', forceauth.exempt(serve), {'document_root': settings.STATIC_ROOT}),
]


# XXX: do not bind to settings.DEBUG, to test working sentry on DEBUG:False
if 'src.userswitcher' in settings.INSTALLED_APPS:
    from django.http import HttpResponse
    import logging

    logger = logging.getLogger(__name__)

    @forceauth.exempt
    def _trigger_log(request):
        logger.warn('debug test message')
        return HttpResponse()

    @forceauth.exempt
    def _403(request):
        return render(request, '403.html', status=403)

    @forceauth.exempt
    def _404(request):
        return render(request, '404.html', status=404)

    @forceauth.exempt
    def _500(request):
        return render(request, '500.html', status=500)

    urlpatterns += [
        path('debug/403/', _403),
        path('debug/404/', _404),
        path('debug/500/', _500),
        path('debug/trigger-log/', _trigger_log),
    ]

if 'src.userswitcher' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('userswitcher/', include('src.userswitcher.urls', namespace='userswitcher')),
    ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls')),
    ]
