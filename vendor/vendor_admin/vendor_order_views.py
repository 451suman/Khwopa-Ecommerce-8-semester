from winreg import DeleteKey
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from products.models import VENDOR_ORDER_STATUS, CartProduct
from vendor.models import Vendor
from vendor.vendor_admin.forms import VendorOrderStatusForm
from vendor.vendor_admin.views import VendorRequiredMixin



class VendorOrderReceivedListView(ListView):
    model = CartProduct
    template_name = "admin_dash/vendor_order/vendor_order_list/vendor_order.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "vendor", "cart", "cart__order")
            .order_by("-id").filter(vendor=self.request.user.vendor, vendor_order_status="Order Received")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = Vendor.objects.get(user=self.request.user)
        context["status_choices"] = VENDOR_ORDER_STATUS
        return context
class VendorOrderProcessingListView(ListView):
    model = CartProduct
    template_name = "admin_dash/vendor_order/vendor_order_list/vendor_order.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "vendor", "cart", "cart__order")
            .order_by("-id").filter(vendor=self.request.user.vendor, vendor_order_status="Order Processing")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = Vendor.objects.get(user=self.request.user)
        context["status_choices"] = VENDOR_ORDER_STATUS
        return context
class VendorOrderwayListView(ListView):
    model = CartProduct
    template_name = "admin_dash/vendor_order/vendor_order_list/vendor_order.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "vendor", "cart", "cart__order")
            .order_by("-id").filter(vendor=self.request.user.vendor, vendor_order_status="On the way")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = Vendor.objects.get(user=self.request.user)
        context["status_choices"] = VENDOR_ORDER_STATUS
        return context
class VendorOrderCompletedListView(ListView):
    model = CartProduct
    template_name = "admin_dash/vendor_order/vendor_order_list/vendor_order.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("product", "vendor", "cart", "cart__order")
            .order_by("-id").filter(vendor=self.request.user.vendor, vendor_order_status="Order Completed")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor"] = Vendor.objects.get(user=self.request.user)
        context["status_choices"] = VENDOR_ORDER_STATUS
        return context
    



class CartProductStatusUpdateView(VendorRequiredMixin, UpdateView):
    model = CartProduct
    form_class = VendorOrderStatusForm
    template_name = "vendor/order_status_update.html"  # not used in modal, but required

    def get_queryset(self):
        # allow vendor to update only their own CartProduct
        vendor = get_object_or_404(Vendor, user=self.request.user)
        return CartProduct.objects.filter(vendor=vendor)

    def form_valid(self, form):
        messages.success(self.request, "Order status updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        # go back to same page after update
        return self.request.META.get("HTTP_REFERER") or reverse_lazy("vendor_orders")
