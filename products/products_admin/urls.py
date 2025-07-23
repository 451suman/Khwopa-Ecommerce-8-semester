from django.urls import path

from products.products_admin.views import DashboardView, ProductListView


urlpatterns = [
    path("home/", DashboardView.as_view(), name="dashboard_admin"),
    path("product-list/", ProductListView.as_view(), name="product_list_admin"),
]
