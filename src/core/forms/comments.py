from django import forms

from src.core.models import Comment


class CommentForm(forms.ModelForm):
    file = forms.FileField(required=False)

    class Meta:
        model = Comment
        fields = ['text', 'file']
