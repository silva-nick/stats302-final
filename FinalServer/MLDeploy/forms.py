from django import forms
from .models import TweetRequest

class TweetRequestForm(forms.ModelForm):
    class Meta:
        model = TweetRequest
        fields='__all__'

    category = forms.CharField(max_length=32)
