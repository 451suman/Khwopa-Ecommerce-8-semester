from rest_framework import serializers
from products.models import (
    Brand,
    Category,
    Color,
    Product,
    ProductImage,
    Size,
    Tag,
)  # Make sure this is the correct model import


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    brand = BrandSerializer()
    colors = ColorSerializer(many=True)
    sizes = SizeSerializer(many=True)
    tag = TagSerializer(many=True)
    # product_images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class NewProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "current_price", "product_images"]


class FeaturedCategorySerializer(serializers.ModelSerializer):
    # Correct the field name to 'products'
    products = NewProductSerializer(many=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "arranged", "products"]
