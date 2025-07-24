from django.urls import path

from products.products_admin.views import AdminProductDetails, DashboardView, ProductListView


urlpatterns = [
    path("home/", DashboardView.as_view(), name="dashboard_admin"),
    path("product-list/", ProductListView.as_view(), name="product_list_admin"),
    path("product-detail/<str:slug>/",AdminProductDetails.as_view(), name="product_detail_admin"),
]
