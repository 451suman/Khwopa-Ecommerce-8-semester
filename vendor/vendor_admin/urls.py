from django.urls import include, path

from vendor.vendor_admin.views import AdminVendorCreateView, AdminVendorDeleteView, AdminVendorListView, AdminVendorUpdateView

urlpatterns = [
    path("vendor/list/", AdminVendorListView.as_view(), name="vendor_list_admin"),
    path("vendor/create/", AdminVendorCreateView.as_view(), name="vendor_create_admin"),
    path("vendor/delete/<int:pk>/", AdminVendorDeleteView.as_view(), name="vendor_delete_admin"),
    path("vendor/<int:pk>/edit/", AdminVendorUpdateView.as_view(), name="vendor_update_admin"),
]
