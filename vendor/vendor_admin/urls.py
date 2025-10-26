from django.urls import include, path

from vendor.vendor_admin.views import AdminVendorListView

urlpatterns = [
    path("vendor/list/", AdminVendorListView.as_view(), name="vendor_list_admin"),
]
