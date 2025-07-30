from django import forms
from django.forms import inlineformset_factory
from products.models import Brand, Category, Color, Product, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "brand",
            "tag",
            "color",
            "sizes",
            "previous_price",
            "current_price",
            "stock",
            "is_active",
            "is_featured",
            "is_custom_price",
        ]


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=("image",),
    extra=1,
    can_delete=True,
    widgets={"image": forms.ClearableFileInput(attrs={"class": "form-control-file"})},
    # No explicit prefix, default is 'productimage_set'
)


class AdminCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["vendor", "name", "arranged"]


class AdminBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["vendor", "name", "logo"]


class AdminColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields ="__all__"