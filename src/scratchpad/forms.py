from django import forms

from src.scratchpad.models import ScratchPad

class ScratchPadForm(forms.ModelForm):
    class Meta:
        model = ScratchPad
        fields = ['text']
