import secrets
import string

# from products.models import Product


def generate_secret_key(length=50):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(chars) for _ in range(length))


# def product_filter_func(request, min, max):
#     products_price_filter = Product.objects.filter(current_price__range=(min, max))

#     return products_price_filter
