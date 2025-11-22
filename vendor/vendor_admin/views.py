from winreg import DeleteKey
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from vendor.models import Vendor
from vendor.vendor_admin.forms import (
    AdminVendorForm,
    VendorUserCreationForm,
    VendorUserEditForm,
)


# Ensure only admin users (staff or superuser) can access this view
class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(
                request, "You must be an admin or staff to access this page."
            )
            return redirect("admin_login")  # Redirect to the admin login page


class VendorRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_vendor):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(
                request, "You must be an admin or staff to access this page."
            )
            return redirect("admin_login")  # Redirect to the admin login page


class AdminVendorListView(AdminRequiredMixin, ListView):
    model = Vendor
    template_name = "admin_dash/vendor/vendorlist.html"
    context_object_name = "vendors"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").order_by("-id")
        search = self.request.GET.get("search", "")
        is_authorized = self.request.GET.get("is_authorized", "")
        if search:
            queryset = queryset.filter(
                vendor_name__icontains=search,
                email__icontains=search,
                phone__icontains=search,
                phone__iexact=search,
            )
        if is_authorized:
            queryset = queryset.filter(is_authorized=is_authorized)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Vendors"
        return context


class AdminVendorDeleteView(AdminRequiredMixin, DeleteView):
    model = Vendor
    context_object_name = "vendor"
    template_name = "admin_dash/vendor/vendorlist.html"

    success_url = reverse_lazy("vendor_list_admin")

    def get_success_url(self):
        messages.success(self.request, "Vendor deleted successfully")

        return super().get_success_url()


class AdminVendorCreateView(AdminRequiredMixin, View):
    template_name = "admin_dash/vendor/vendor_create_edit_form.html"
    success_url = reverse_lazy("vendor_list_admin")

    def get(self, request, *args, **kwargs):
        user_form = VendorUserCreationForm()
        vendor_form = AdminVendorForm()
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "vendor_form": vendor_form},
        )

    def post(self, request, *args, **kwargs):
        user_form = VendorUserCreationForm(request.POST)
        vendor_form = AdminVendorForm(request.POST, request.FILES)

        if user_form.is_valid() and vendor_form.is_valid():
            user = user_form.save(commit=False)
            user.is_vendor = True  # if you have a field to mark vendors
            user.save()

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.email = user.email
            vendor.phone = user.phone
            vendor.address = user.address
            vendor.save()

            messages.success(request, "Vendor and user created successfully.")
            return redirect(self.success_url)

        messages.error(request, "Please correct the errors below.")
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "vendor_form": vendor_form},
        )


class AdminVendorUpdateView(AdminRequiredMixin, View):
    template_name = "admin_dash/vendor/vendor_create_edit_form.html"
    success_url = reverse_lazy("vendor_list_admin")

    def get(self, request, pk, *args, **kwargs):
        vendor = get_object_or_404(Vendor, pk=pk)
        user = vendor.user

        user_form = VendorUserEditForm(instance=user)
        vendor_form = AdminVendorForm(instance=vendor)

        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "vendor_form": vendor_form,
                "is_update": True,
            },
        )

    def post(self, request, pk, *args, **kwargs):
        vendor = get_object_or_404(Vendor, pk=pk)
        user = vendor.user

        user_form = VendorUserEditForm(request.POST, instance=user)
        vendor_form = AdminVendorForm(request.POST, request.FILES, instance=vendor)

        if user_form.is_valid() and vendor_form.is_valid():
            user_form.save()
            vendor_form.save()

            messages.success(request, "Vendor updated successfully.")
            return redirect(self.success_url)

        messages.error(request, "Please correct the errors below.")
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "vendor_form": vendor_form,
                "is_update": True,
            },
        )
