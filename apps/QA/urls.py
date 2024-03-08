from django.urls import path
from apps.QA.views import FirstView

urlpatterns = [
    path('', FirstView.as_view(), name="index"),  # 类视图后必须加as_view()
]
