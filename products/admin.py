from django.contrib import admin
from .models import Category, Brand, Color, Size, Tag, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "arranged")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("vendor",)
    search_fields = ("name",)
    ordering = ("arranged",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    list_filter = ("vendor",)
    search_fields = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    list_filter = ("vendor",)
    search_fields = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    list_filter = ("vendor",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor")
    list_filter = ("vendor",)
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# class ProductVariantInline(admin.TabularInline):
#     model = ProductVariant
#     extra = 1
#     fields = ('color', 'size', 'stock', 'previous_price', 'current_price')
#     autocomplete_fields = ('color', 'size')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "category", "brand", "is_active", "is_featured")
    list_filter = ("vendor", "category", "brand", "is_active", "is_featured")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tag", "sizes")

    inlines = [ProductImageInline]


# @admin.register(ProductVariant)
# class ProductVariantAdmin(admin.ModelAdmin):
#     list_display = ('product', 'color', 'size', 'stock', 'current_price')
#     list_filter = ('product', 'color', 'size')
#     search_fields = ('product__name',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image")
    list_filter = ("product",)
    search_fields = ("product__name",)


from django.contrib import admin
from .models import Cart, CartProduct, Order, Review


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "created_a")
    search_fields = ("user__username",)
    list_filter = ("created_a",)


@admin.register(CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "rate", "quantity", "subtotal")
    search_fields = ("product__name",)
    list_filter = ("cart",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "user",
        "ordered_by",
        "shipping_address",
        "mobile",
        "email",
        "subtotal",
        "discount",
        "total",
        "order_status",
        "created_at",
    )
    list_filter = ("order_status", "created_at")
    search_fields = ("ordered_by", "shipping_address", "mobile", "email")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "rating", "created_at")
    search_fields = ("user__username", "product__name")
    list_filter = ("rating", "created_at")

    # def user(self, obj):
    #     return obj.user.full_name

    # def product(self, obj):
    #     return obj.product.title
