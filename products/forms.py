from django import forms

from products.models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["user", "ordered_by", "shipping_address", "mobile", "email"]

    def clean_mobile(self):
        mob = self.cleaned_data["mobile"]
        if len(mob) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mob
