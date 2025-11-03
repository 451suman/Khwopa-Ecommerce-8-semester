from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from .forms import AdminLoginForm  # your form import


class AdminLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("admin_login")


class AdminLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and (
            request.user.is_superuser
            or request.user.is_staff
            or request.user.is_vendor
            or getattr(request.user, "is_vendor", False)
        ):
            return redirect("dashboard_admin")
        form = AdminLoginForm()
        return render(request, "admin_dash/login/admin_login.html", {"form": form})

    def post(self, request):
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None and (
                user.is_superuser
                or user.is_staff
                or user.is_vendor
                or getattr(user, "is_vendor", False)
            ):
                login(request, user)
                return redirect("dashboard_admin")  # change to your dashboard route
            else:
                form.add_error(
                    None, "Invalid email or password or you do not have access."
                )

        return render(request, "admin_dash/login/admin_login.html", {"form": form})
