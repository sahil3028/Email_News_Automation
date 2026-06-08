from django import forms

from .models import Recipient


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["name", "email"]


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class CampaignForm(forms.Form):
    topic = forms.CharField(max_length=160)
