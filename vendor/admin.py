from django.contrib import admin

from vendor.models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("vendor_name", "email", "phone", "address", "arranged", "is_active", "is_authorized")
    search_fields = ("vendor_name", "email", "phone", "address", "pan_no", "reg_no")
    list_filter = ("created_at", "is_authorized", "is_active", "is_verified")
    ordering = ("-arranged",)
    date_hierarchy = "created_at"
    prepopulated_fields = {"slug": ("vendor_name",)}


