from django import forms
from apps.utils import parameters


class questionForm(forms.Form):
    """
    表单验证
    """
    question = forms.CharField(required=True, max_length=parameters()['max_length'])
    MODELS_CHOICES = {"gpt-3.5-turbo": "gpt-3.5-turbo"}
    FUNCTION_CHOICE = {"LLM问答": 1, "结合知识库问答": 2}
    model = forms.ChoiceField(required=True, choices=MODELS_CHOICES)
    function = forms.ChoiceField(required=True, choices=FUNCTION_CHOICE)
    temperature = forms.DecimalField(required=True, max_value=5, min_value=0)
