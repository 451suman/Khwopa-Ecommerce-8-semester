from django.db import models
from common.models import TimeStampedModel
from common.utils import generate_secret_key

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Vendor(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    vendor_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    pan_no = models.CharField(max_length=15)
    reg_no = models.CharField(max_length=15)
    is_authorized = models.BooleanField(default=False)
    shop_image = models.ImageField(upload_to="vendor/shop/", null=True, blank=True)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    access_key = models.CharField(max_length=255, null=True, blank=True)
    citizenship = models.CharField(max_length=255, null=True, blank=True)
    arranged = models.PositiveIntegerField(null=True, blank=True)

    citizenship_front_image = models.ImageField(
        upload_to="vendor/citizenship/", null=True, blank=True
    )
    citizenship_back_image = models.ImageField(
        upload_to="vendor/citizenship/", null=True, blank=True
    )
    vendor_profile = models.ImageField(
        upload_to="vendor/profile/", null=True, blank=True
    )
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    slug = models.SlugField(unique=False, null=True, blank=True)

    def __str__(self):
        return self.vendor_name

    class Meta:
        ordering = ["-pan_no"]
        indexes = [
            models.Index(fields=["pan_no"]),
        ]

def save(self, *args, **kwargs):
    if not self.secret_key:
        self.secret_key = generate_secret_key()
    if not self.access_key:
        self.access_key = generate_secret_key()
    if not self.slug:
        base_slug = slugify(self.vendor_name)
        slug = base_slug
        counter = 1
        while Vendor.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
    super().save(*args, **kwargs)
