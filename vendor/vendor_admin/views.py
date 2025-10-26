from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView
from vendor.models import Vendor

# Ensure only admin users (staff or superuser) can access this view
class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "You must be an admin or staff to access this page.")
            return redirect("admin_login")  # Redirect to the admin login page

class AdminVendorListView(AdminRequiredMixin, ListView):
    model = Vendor
    template_name = "admin_dash/vendor/vendorlist.html"
    context_object_name = "vendors"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").order_by("-id")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Vendors"
        return context