from django.template import Library
#from django.contrib.messages import get_messages

# register = Library()


# @register.filter
# def level2alert(lvl):
#     '''
#     Translate django.contrib.auth message levels to bootstrap alert classes.
#     '''
#     tr = {
#         get_messages.SUCCESS: 'success',
#         get_messages.WARNING: 'warning',
#         get_messages.ERROR: 'danger',
#     }
#     return tr.get(lvl, 'info')


from django import template
from django.contrib.messages import get_messages, constants

register = template.Library()

@register.filter
def level2alert(lvl):
    '''
    Translate django.contrib.auth message levels to bootstrap alert classes.
    '''
    tr = {
        constants.SUCCESS: 'success',
        constants.WARNING: 'warning',
        constants.ERROR: 'danger',
    }
    return tr.get(lvl, 'info')
