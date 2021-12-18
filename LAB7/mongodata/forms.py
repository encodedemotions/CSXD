from django import forms


class DataForm(forms.Form):
    data = forms.CharField(max_length=256)
