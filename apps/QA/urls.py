from django.urls import path
from apps.QA.views import FirstView, knowladgeManagementView

urlpatterns = [
    path('', FirstView.as_view(), name="index"),  # 类视图后必须加as_view()
    path('km/', knowladgeManagementView.as_view(), name="km")
]
