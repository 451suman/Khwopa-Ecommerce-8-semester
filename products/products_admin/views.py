from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

from accounts import models
from products.models import CartProduct, Order, Product, Review
from django.db.models import Sum, Q
User = get_user_model()
from django.db.models import Sum, Q
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardView(TemplateView):
    template_name = "admin_dash/dashboard/dashboard.html"  # fixed typo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_count"] = User.objects.count()

        context["recent_reviews"] = Review.objects.select_related(
            "user", "product"
        ).prefetch_related(
            "product__product_images"
        ).order_by("-created_at")[:6]

        context["orders"] = Order.objects.select_related("user").all()

        # Define the completed_orders queryset
        completed_orders = Order.objects.filter(order_status="Order Completed")

        # Query top 9 best selling products based on completed orders
        cart_products = CartProduct.objects.filter(cart__order__order_status="Order Completed")
        top_products_data = (
            cart_products
            .values('product')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:9]
        )

        product_ids = [item['product'] for item in top_products_data]
        products = Product.objects.filter(id__in=product_ids)

        sold_map = {item['product']: item['total_sold'] for item in top_products_data}
        for product in products:
            product.total_sold = sold_map.get(product.id, 0)
        breakpoint()
        context["best_selling_products"] = products
        return context

