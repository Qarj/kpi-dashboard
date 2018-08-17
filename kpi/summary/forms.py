from django import forms

class EditForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)

