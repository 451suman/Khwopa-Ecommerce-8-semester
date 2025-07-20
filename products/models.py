from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser
from common.models import TimeStampedModel  # Created/Updated timestamp
from vendor.models import Vendor


class Category(TimeStampedModel):
    ARRANGE_CHOICES = [(i, str(i)) for i in range(1, 7)]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    arranged = models.PositiveIntegerField(
        choices=ARRANGE_CHOICES, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Brand(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="brands_logo/", null=True, blank=True)

    def __str__(self):
        return self.name


class Color(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Size(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=10)  # e.g., S, M, L or 42, 44

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_custom_price = models.BooleanField(default=False, null=True, blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    tag = models.ManyToManyField(Tag, blank=True, related_name="products")

    # Fallback prices (used if variant pricing not available)
    previous_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # ManyToMany to Size directly (for global size availability)
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="products_colour",
    )
    # In Product model

    sizes = models.ManyToManyField(
        Size,
        blank=True,
        related_name="products_with_multiple_sizes",  # 👈 reverse relation name for M2M
    )

    stock = models.PositiveIntegerField(default=0, null=True, blank=True)

    # Colors handled through ProductVariant
    # colors = models.ManyToManyField(Color, through="ProductVariant", related_name="products")

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # def get_price_for(self, color=None, size=None):
    #     try:
    #         variant = ProductVariant.objects.get(product=self, color=color, size=size)
    #         return variant.current_price or self.current_price
    #     except ProductVariant.DoesNotExist:
    #         return self.current_price


# class ProductVariant(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
#     color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
#     size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
#     stock = models.PositiveIntegerField(default=0, null=True, blank=True)

#     previous_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#     class Meta:
#         unique_together = ("product", "color", "size")
#         verbose_name = "Product Variant"
#         verbose_name_plural = "Product Variants"

#     def __str__(self):
#         parts = [self.product.name]
#         if self.color: parts.append(self.color.name)
#         if self.size: parts.append(self.size.name)
#         return " - ".join(parts)


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return f"{self.product.name} image"


class Cart(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    total = models.PositiveBigIntegerField(default=0)
    created_a = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart:" + str(self.id)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart:" + str(self.cart.id) + "CartProduct: " + str(self.id)


ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    ordered_by = models.CharField(max_length=50)  #
    shipping_address = models.CharField(max_length=60)  #
    mobile = models.CharField(max_length=10)  #
    email = models.EmailField(null=True, blank=True)  #
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(
        max_length=50, choices=ORDER_STATUS, default="Order Received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order: " + str(self.id)


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(null=True, blank=True)
    # Assuming a rating scale of 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.full_name} for {self.product.name}"
