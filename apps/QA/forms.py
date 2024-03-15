from django import forms
from apps.utils import parameters
import os


class questionForm(forms.Form):
    """
    表单验证
    """
    question = forms.CharField(required=True, max_length=parameters()['max_length'])
    filenames = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")
    model = forms.CharField(required=True)
    db = forms.CharField(required=False)
    temperature = forms.DecimalField(required=True, max_value=1, min_value=0)


class dbForm(forms.Form):
    file_ = forms.FileField(required=True)
    chunk_size = forms.DecimalField(required=True)
    chunk_overlap = forms.DecimalField(required=True)
    db = forms.CharField(required=True)
    kname = forms.CharField(required=True)
