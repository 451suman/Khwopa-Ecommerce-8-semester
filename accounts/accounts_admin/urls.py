from django.urls import path

from accounts.accounts_admin.views import DashboardView


urlpatterns = [
   path("dashboard/",DashboardView.as_view(),name="dashboard"),
]
