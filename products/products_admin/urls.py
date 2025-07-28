from django.urls import path

from products.products_admin.views import AdminProductDetails, DashboardView, ProductCreateView, ProductListView, ProductUpdateView


urlpatterns = [
    path("home/", DashboardView.as_view(), name="dashboard_admin"),
    path("product-list/", ProductListView.as_view(), name="product_list_admin"),
    path("product-detail/<str:slug>/",AdminProductDetails.as_view(), name="product_detail_admin"),
    path("product/add/", ProductCreateView.as_view(), name="product_add"),
     path("product/<slug:slug>/edit/", ProductUpdateView.as_view(), name="product_update"),
    # path("product/<slug:slug>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]
