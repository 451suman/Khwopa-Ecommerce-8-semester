from django.urls import path

from products.products_admin.views import DashboardView


urlpatterns = [
      path("dashboard/",DashboardView.as_view(),name="dashboard_admin"),

]
