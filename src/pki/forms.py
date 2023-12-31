from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.db.models import Q

from src.core.forms.fields import AutocompleteModelChoiceField
from src.pki.models import Certificate


class CertForm(forms.Form):
    # user = AutocompleteModelChoiceField(
    #     'pki-users',
    #     User.objects.filter(
    #         Q(profile__is_internal=True) | Q(profile__is_omniscient_member=True),
    #         is_active=True
    #     )
    # )
    #user= forms.ModelChoiceField(queryset=User.objects.all())
    user= forms.ModelChoiceField(queryset=User.objects.filter(
             Q(profile__is_internal=True) | Q(profile__is_omniscient_member=True),
             is_active=True
         ))
    cn = forms.CharField(max_length=64)
    
    def clean(self):
        cd = super().clean()
        
        user = cd.get('user')
        if user:
            cn = cd.get('cn')
            if Certificate.objects.filter(cn=cn).exists():
                self.add_error('cn', _('A certificate with this CN already exists.'))

        return cd

# from django import forms
# from django_select2.forms import ModelSelect2Widget
# from django.contrib.auth.models import User

# class CertForm(forms.Form):
#     user= forms.ModelChoiceField(queryset=User.objects.all())
    
#     print(f"user is ------>{user}")
#     cn = forms.CharField(max_length=64)

#     def clean(self):
#         cd = super().clean()

#         user = cd.get('user')
#         if user:
#             cn = cd.get('cn')
#             if Certificate.objects.filter(cn=cn).exists():
#                 self.add_error('cn', _('A certificate with this CN already exists.'))

#         return cd
