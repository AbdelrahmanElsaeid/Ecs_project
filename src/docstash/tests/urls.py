import json

from django.urls import path
from django.http import HttpResponse
from src.docstash.decorators import with_docstash


@with_docstash()
def simple_post_view(request):
    if request.method == 'POST':
        request.docstash.value = request.POST.dict()
        request.docstash.save()
    return HttpResponse(json.dumps(request.docstash.value), content_type='text/json')

urlpatterns = (
    path('simple_post/(<int:docstash_key>)', simple_post_view),
)