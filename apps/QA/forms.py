from django import forms
from apps.utils import parameters
import os


class questionForm(forms.Form):
    """
    表单验证
    """
    question = forms.CharField(required=True, max_length=parameters()['max_length'])
    # MODELS_CHOICES = {"gpt-3.5-turbo": "gpt-3.5-turbo", "qianfan": "百度千帆大模型"}
    filenames = os.listdir("D:\\MyPyCharm\\PrivateDocAssistant\\apps\\QA\\VectorStore")
    # DB_CHOICE = {}
    # for db in filenames:
    #     tempdict = {db: db}
    #     DB_CHOICE.update(tempdict)
    model = forms.CharField(required=True)
    db = forms.CharField(required=True)
    temperature = forms.DecimalField(required=True, max_value=1, min_value=0)
