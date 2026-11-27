from django import forms
from .models import Transcription

class TranscriptionForm(forms.ModelForm):
    class Meta:
        model = Transcription
        fields = ["title", "text", "language"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 7}),
            "language": forms.TextInput(attrs={"class": "form-control"}),
        }
