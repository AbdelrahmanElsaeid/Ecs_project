from django.template import Library
from django.conf import settings

from src.userswitcher.forms import UserSwitcherForm
from src.userswitcher import SESSION_KEY

register = Library()

if settings.ECS_USERSWITCHER_ENABLED:
    @register.inclusion_tag('userswitcher/form.html', takes_context=True)
    def userswitcher(context):
        request = context['request']
        return {
            'form': UserSwitcherForm({'user': request.session.get(SESSION_KEY)}),
            'url': request.get_full_path(),
        }
else:
    @register.simple_tag
    def userswitcher():
        return ''
