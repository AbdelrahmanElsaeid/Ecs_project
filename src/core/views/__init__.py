from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control
from django.templatetags.static import static
from src.core.models import AdvancedSettings
from src.utils import forceauth


@forceauth.exempt
@cache_control(max_age=3600)
def logo(request):
    s = AdvancedSettings.objects.first()  # Assuming you want to retrieve the first instance

    if not s or not s.logo:
        fallback_logo_url = static('images/fallback_logo.png')
        return redirect(fallback_logo_url)

    return HttpResponse(s.logo, content_type=s.logo_mimetype)















