from django.shortcuts import render
from django.views.generic.base import View


class FirstView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")
    
    def post(self, request, *args, **kwargs):
        pass