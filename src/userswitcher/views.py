from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect

from src.userswitcher.forms import UserSwitcherForm
from src.userswitcher import SESSION_KEY


def switch(request):
    form = UserSwitcherForm(request.POST)
    if form.is_valid():
        request.session[SESSION_KEY] = getattr(form.cleaned_data.get('user'), 'pk', None)
    # request.GET.get('url', '/')
    return redirect('dashboard:view_dashboard')