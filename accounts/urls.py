from django.urls import path

from .views import ExpenseMateLoginView, ExpenseMateLogoutView

urlpatterns = [
    path("login/", ExpenseMateLoginView.as_view(), name="login"),
    path("logout/", ExpenseMateLogoutView.as_view(), name="logout"),
]
