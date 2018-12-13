from django import forms

class EditForm(forms.Form):
    report_period_days = forms.CharField(widget=forms.TextInput)

class EndpointForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)
    secret = forms.CharField(widget=forms.TextInput)
    queue_url = forms.CharField(widget=forms.TextInput)
    get_url = forms.CharField(widget=forms.TextInput)
    default_report_suite_id = forms.CharField(widget=forms.TextInput)
    default_report_period_days = forms.CharField(widget=forms.TextInput)
