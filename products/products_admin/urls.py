from django.urls import path

from products.products_admin.views import (
    AdminOrderCanceledView,
    AdminOrderCompletedView,
    AdminOrderDetailView,
    AdminOrderFilteredView,
    AdminOrderOnTheWayView,
    AdminOrderProcessingView,
    AdminOrderReceivedView,
    AdminProductDetails,
    BrandADminDeleteView,
    BrandAdminCreateView,
    BrandAdminListView,
    BrandAdminUpdateView,
    CategoryAdminCreateView,
    CategoryAdminDeleteView,
    CategoryAdminListView,
    CategoryAdminUpdateView,
    ColorAdminDeleteView,
    ColorAdminListView,
    ColorAdminUpdateView,
    ColourAdminCreateView,
    DashboardView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductUpdateView,
    SizeAdminCreateView,
    SizeAdminDeleteView,
    SizeAdminListView,
    SizeAdminUpdateView,
    TagAdminCreateView,
    TagAdminDeleteView,
    TagAdminListView,
    TagAdminUpdateView,
    admin_change_order_status,
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
    path(
        "brand/<int:id>/edit/",
        BrandAdminUpdateView.as_view(),
        name="brand_update_admin",
    ),
    path(
        "brand/<int:id>/delete/",
        BrandADminDeleteView.as_view(),
        name="brand_delete_admin",
    ),
    # color crud
    path("color/", ColorAdminListView.as_view(), name="color_list_admin"),
    path("color/add/", ColourAdminCreateView.as_view(), name="color_add_admin"),
    path(
        "color/<int:id>/edit/",
        ColorAdminUpdateView.as_view(),
        name="color_update_admin",
    ),
    path(
        "color/<int:id>/delete/",
        ColorAdminDeleteView.as_view(),
        name="color_delete_admin",
    ),
    # size crud
    path("size/", SizeAdminListView.as_view(), name="size_list_admin"),
    path("size/add/", SizeAdminCreateView.as_view(), name="size_add_admin"),
    path(
        "size/<int:id>/edit/", SizeAdminUpdateView.as_view(), name="size_update_admin"
    ),
    path(
        "size/<int:id>/delete/",
        SizeAdminDeleteView.as_view(),
        name="size_delete_admin",
    ),
    # tags
    path("tag/", TagAdminListView.as_view(), name="tag_list_admin"),
    path("tag/add/", TagAdminCreateView.as_view(), name="tag_add_admin"),
    path("tag/<int:id>/edit/", TagAdminUpdateView.as_view(), name="tag_update_admin"),
    path(
        "tag/<int:id>/delete/",
        TagAdminDeleteView.as_view(),
        name="tags_delete_admin",
    ),
    # order
    
    path(
        "order/filtered/",
        AdminOrderFilteredView.as_view(),
        name="admin_order_filtered_list",
    ),
    path(
        "order/received/",
        AdminOrderReceivedView.as_view(),
        name="admin_order_received_list",
    ),
    path(
        "order/proessing/",
        AdminOrderProcessingView.as_view(),
        name="admin_order_processing_list",
    ),
    path(
        "order/on-the-way/",
        AdminOrderOnTheWayView.as_view(),
        name="admin_order_ontheway_list",
    ),
    path(
        "order/completed/",
        AdminOrderCompletedView.as_view(),
        name="admin_order_complete_list",
    ),
    path(
        "order/cancelled/",
        AdminOrderCanceledView.as_view(),
        name="admin_order_cancelled_list",
    ),
    path(
        "order/details/<str:order_number>/",
        AdminOrderDetailView.as_view(),
        name="admin_order_details",
    ),
    path("admin-order-change-status-<int:pk>", admin_change_order_status, name="admin-order-change-status"),
]
