from django.urls import include, path

from vendor.vendor_admin.vendor_order_views import (
    CartProductStatusUpdateView,
    VendorOrderCompletedListView,
    VendorOrderProcessingListView,
    VendorOrderReceivedListView,
    VendorOrderwayListView,
)
from vendor.vendor_admin.views import (
    AdminVendorCreateView,
    AdminVendorDeleteView,
    AdminVendorListView,
    AdminVendorUpdateView,
)

urlpatterns = [
    # create vendor by admin
    path("vendor/list/", AdminVendorListView.as_view(), name="vendor_list_admin"),
    path("vendor/create/", AdminVendorCreateView.as_view(), name="vendor_create_admin"),
    path(
        "vendor/delete/<int:pk>/",
        AdminVendorDeleteView.as_view(),
        name="vendor_delete_admin",
    ),
    path(
        "vendor/<int:pk>/edit/",
        AdminVendorUpdateView.as_view(),
        name="vendor_update_admin",
    ),
    # vendor user order crud
    path(
        "order/list/received/",
        VendorOrderReceivedListView.as_view(),
        name="vendor_order_list_admin",
    ),
    path(
        "order/list/processing/",
        VendorOrderProcessingListView.as_view(),
        name="vendor_order_list_admin_processing",
    ),
    path(
        "order/list/way/",
        VendorOrderwayListView.as_view(),
        name="vendor_order_list_admin_way",
    ),
    path(
        "order/list/completed/",
        VendorOrderCompletedListView.as_view(),
        name="vendor_order_list_admin_completed",
    ),
    path(
        "vendor/order-item/<int:pk>/status/",
        CartProductStatusUpdateView.as_view(),
        name="vendor_cartproduct_status_update",
    ),
]
