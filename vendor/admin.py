# admin.py
from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("vendor_name", "email", "phone", "address", "arranged")
    search_fields = ("vendor_name", "email", "phone", "address")
    list_filter = ("created_at", "is_authorized", "arranged")
    ordering = ("-arranged",)
    date_hierarchy = "created_at"
