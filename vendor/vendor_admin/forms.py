from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from products.models import CartProduct
from vendor.models import Vendor


class VendorUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "phone", "address", "password1", "password2")


class AdminVendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
"vendor_name",
"email",
"phone",
"address",
"pan_no",
"reg_no",
"is_authorized",
"shop_image",
"citizenship",
"arranged",
        ]



class VendorUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "phone", "address", "is_active")
        
# ----------------------------------------------------------


class VendorOrderStatusForm(forms.ModelForm):
    class Meta:
        model = CartProduct
        fields = ["vendor_order_status"]
        widgets = {
            "vendor_order_status": forms.Select(attrs={
                "class": "form-select"
            })
        }