from django import forms
from django.forms import inlineformset_factory
from products.models import Brand, Category, Color, Product, ProductImage, Size, Tag
from vendor.models import Vendor


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "vendor",
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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Pop user from kwargs
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_vendor:
                # Hide vendor field and set it in the view
                self.fields["vendor"].widget = forms.HiddenInput()
                self.fields["vendor"].required = False
            elif self.user.is_superuser or self.user.is_staff:
                # Admin: Show all vendors
                self.fields["vendor"].queryset = Vendor.objects.all()


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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_vendor:
                # Hide vendor field and set it in the view
                self.fields["vendor"].widget = forms.HiddenInput()
                self.fields["vendor"].required = False
                self.fields["arranged"].widget = forms.HiddenInput()  # ✅ Corrected
                self.fields["arranged"].required = (
                    False  # ✅ Optional if you want to make it optional
                )

            elif self.user.is_superuser or self.user.is_staff:
                # Admin: Show all vendors
                self.fields["vendor"].queryset = Vendor.objects.all()


class AdminBrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["vendor", "name", "logo"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Pop user from kwargs passed form views
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_vendor:
                # Hide vendor field and set it in the view
                self.fields["vendor"].widget = forms.HiddenInput()
                self.fields["vendor"].required = False
            elif self.user.is_superuser or self.user.is_staff:
                self.fields["vendor"].queryset = Vendor.objects.all()


class AdminColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Pop user from kwargs
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_vendor:
                # Hide vendor field and set it in the view
                self.fields["vendor"].widget = forms.HiddenInput()
                self.fields["vendor"].required = False
            elif self.user.is_superuser or self.user.is_staff:
                # Admin: Show all vendors
                self.fields["vendor"].queryset = Vendor.objects.all()


class AdminSizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Pop user from kwargs passed form views
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_vendor:
                # Hide vendor field and set it in the view
                self.fields["vendor"].widget = forms.HiddenInput()
                self.fields["vendor"].required = False
            elif self.user.is_superuser or self.user.is_staff:
                self.fields["vendor"].queryset = Vendor.objects.all()




class AdminTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Pop user from kwargs passed form views
        super().__init__(*args, **kwargs)

        if self.user:
            if self.user.is_vendor:
                # Hide vendor field and set it in the view
                self.fields["vendor"].widget = forms.HiddenInput()
                self.fields["vendor"].required = False
            elif self.user.is_superuser or self.user.is_staff:
                self.fields["vendor"].queryset = Vendor.objects.all()

