from django.contrib import admin

from accounts.models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "is_vendor",
        "is_admin",
        "is_verified",
        "phone",
        "address",
        "date_joined",
    )
    search_fields = ("email", "full_name")
    list_filter = ("is_active", "is_staff", "is_vendor", "is_admin", "is_verified")
