from django.urls import path

from .views import GroupCreateView, GroupListView

urlpatterns = [
    path("", GroupListView.as_view(), name="group_list"),
    path("create/", GroupCreateView.as_view(), name="group_create"),
]
