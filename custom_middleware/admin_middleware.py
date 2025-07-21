from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages  # 🔥 import this

class AdminOrVendor:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request path starts with a protected admin/vendor path
        if request.path.startswith("/account-admin") or request.path.startswith("/product-admin"):
            user = request.user

            # Redirect unauthenticated users to login with a message
            if not user.is_authenticated:
                messages.warning(request, "Please log in to access this section.")
                return redirect(reverse("customer_login"))

            # Redirect unauthorized users with a message
            if not (user.is_admin or user.is_vendor):
                messages.error(request, "You do not have permission to access this section.")
                return redirect(reverse("not-authorized"))

        # Continue processing request
        return self.get_response(request)
