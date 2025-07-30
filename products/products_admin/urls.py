from django.urls import path

from products.products_admin.views import (
    AdminProductDetails,
    BrandADminDeleteView,
    BrandAdminCreateView,
    BrandAdminListView,
    BrandAdminUpdateView,
    CategoryAdminCreateView,
    CategoryAdminDeleteView,
    CategoryAdminListView,
    CategoryAdminUpdateView,
    DashboardView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductUpdateView,
)


urlpatterns = [
    path("home/", DashboardView.as_view(), name="dashboard_admin"),
    # procuct crud
    path("product-list/", ProductListView.as_view(), name="product_list_admin"),
    path(
        "product-detail/<str:slug>/",
        AdminProductDetails.as_view(),
        name="product_detail_admin",
    ),
    path("product/add/", ProductCreateView.as_view(), name="product_add"),
    path(
        "product/<slug:slug>/edit/", ProductUpdateView.as_view(), name="product_update"
    ),
    path(
        "product/<slug:slug>/delete/",
        ProductDeleteView.as_view(),
        name="product_delete",
    ),
    # category crud
    path("category/", CategoryAdminListView.as_view(), name="category_list_admin"),
    path("category/add/", CategoryAdminCreateView.as_view(), name="category_add_admin"),
    path(
        "category/<slug:slug>/edit/",
        CategoryAdminUpdateView.as_view(),
        name="category_update_admin",
    ),
    path(
        "category/<slug:slug>/delete/",
        CategoryAdminDeleteView.as_view(),
        name="category_delete_admin",
    ),
    # brand crud
    path("brand/", BrandAdminListView.as_view(), name="brand_list_admin"),
    path("brand/add/", BrandAdminCreateView.as_view(), name="brand_add_admin"),
    path("brand/<int:id>/edit/", BrandAdminUpdateView.as_view(), name="brand_update_admin"),
    path("brand/<int:id>/delete/", BrandADminDeleteView.as_view(), name="brand_delete_admin"),

    #color crud
    path("color/", BrandAdminListView.as_view(), name="color_list_admin"),
    path("color/add/", BrandAdminCreateView.as_view(), name="color_add_admin"),
    path("color/<int:id>/edit/", BrandAdminUpdateView.as_view(), name="color_update_admin"),
    path("color/<int:id>/delete/", BrandADminDeleteView.as_view(), name="color_delete_admin"),
]
