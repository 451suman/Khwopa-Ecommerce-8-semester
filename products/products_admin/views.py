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


        # Query top 9 best selling products based on completed orders

        new_orders = Order.objects.filter(order_status="Order Received")        
        context["new_orders"] = new_orders
        return context

