from django.urls import path

from accounts.accounts_admin.views import AdminLoginView

urlpatterns = [
    path("login", AdminLoginView.as_view(), name="admin_login"),
]
