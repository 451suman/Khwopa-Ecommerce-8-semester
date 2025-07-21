from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView

from accounts import models
from django.contrib.auth import get_user_model

from products.models import Order, Product, Review

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


# views.py
from django.views.generic import ListView
from products.models import Product
from django.db.models import Prefetch, Avg, Count, Q

class ProductListView(ListView):
    model = Product
    template_name = "admin_dash/productlist/productlist.html"
    context_object_name = "products"
    paginate_by = 5

    def get_queryset(self):
        queryset = Product.objects.prefetch_related("product_images", "review_set")
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = queryset
            
        elif hasattr(user, "vendor") and user.vendor:
            queryset = queryset.filter(vendor=user.vendor)
        else:
            return Product.objects.none()

        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return queryset.annotate(
            avg_rating=Avg("review__rating"),
            review_count=Count("review")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        return context
