from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Prefetch

from products.models import Product, Category, Color
from products.api.serializers import (
    NewProductSerializer,
    FeaturedCategorySerializer,
)


class HomeApiView(APIView):
    def get(self, request):
        # Cache new_products queryset serialized data
        new_products_data = cache.get("new_products_data")
        if not new_products_data:
            new_products_qs = (
                Product.objects.prefetch_related("product_images")
                .filter(is_active=True)
                .order_by("-created_at")[:5]
            )
            new_products_data = NewProductSerializer(new_products_qs, many=True).data
            # cache.set("new_products_data", new_products_data, 60)

        # Cache categories with their prefetched products serialized data
        categories_data = cache.get("categories_data")
        if not categories_data:
            product_qs = Product.objects.filter(is_active=True).prefetch_related(
                "product_images"
            )
            categories_qs = (
                Category.objects.filter(arranged__isnull=False)
                .order_by("arranged")
                .prefetch_related(Prefetch("products", queryset=product_qs))
            )
            categories_data = FeaturedCategorySerializer(categories_qs, many=True).data
            # cache.set("categories_data", categories_data, 60)

        return Response(
            {
                "new_products": new_products_data,
                "categories": categories_data,
            }
        )


# no of queries in DB
# | no| Query purpose                           | Notes                                                                   |
# | - | --------------------------------------- | ----------------------------------------------------------------------- |
# | 1 | Session check: `django_session`         | Checks if user session is valid (common)                                |
# | 2 | User lookup: `accounts_customuser`      | Looks up current user by id                                             |
# | 3 | Fetch new products                      | `products_product` active, ordered by created\_at, limit 5              |
# | 4 | Fetch images for new products           | `products_productimage` for products with IDs in (10,9,8,7,6)           |
# | 5 | Fetch categories                        | Categories with non-null `arranged`, ordered by `arranged`              |
# | 6 | Fetch active products in categories     | Filter products by active + category id in (1,7,2,3,4), ordered by name |
# | 7 | Fetch images for products in categories | Images for product IDs in (5,4,7,3,1,9,2,6)                             |
