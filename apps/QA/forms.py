from django import forms
from apps.utils import parameters


class questionForm(forms.Form):
    """
    表单验证
    """
    question = forms.CharField(required=True, max_length=parameters()['max_length'])
