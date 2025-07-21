from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts import models
from django.contrib.auth import get_user_model

from products.models import Order, Review

User = get_user_model()

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and (models.CustomUser.objects.get(email=request.user.email).is_vendor
                 or request.user.is_staff
                 or request.user.is_superuser)
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "You must be an admin, vendor, or staff to access this page.")
            return redirect("admin_login")


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = "admin_dash/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_count"] = User.objects.count()
        context["recent_reviews"] = Review.objects.select_related(
            "user", "product"
        ).prefetch_related(
            "product__product_images"
        ).order_by("-created_at")[:6]
        context["orders"] = Order.objects.select_related("user").all()
        context["new_orders"] = Order.objects.filter(order_status="Order Received")
        return context
