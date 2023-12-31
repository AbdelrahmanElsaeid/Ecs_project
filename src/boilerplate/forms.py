from django import forms
from django.utils.translation import gettext_lazy as _

from src.boilerplate.models import Text

class TextForm(forms.ModelForm):
    slug = forms.CharField(max_length=Text._meta.get_field('slug').max_length, label=_('Shorthand Symbol'))

    class Meta:
        model = Text
        fields = ('slug', 'text')