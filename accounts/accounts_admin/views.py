from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from .forms import AdminLoginForm  # your form import
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import UserUpdateForm

User = get_user_model()

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



# views.py
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserListView(ListView):
    model = User
    template_name = "admin_dash/user/user_list/user_list.html"
    context_object_name = "objs"   # so it matches your template's `{% for obj in objs %}`
    paginate_by = 10
    ordering = ["-date_joined"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")

        if q:
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(email__icontains=q)
                | Q(phone__icontains=q)
            )

        return qs




class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    pk_url_kwarg = "id"
    template_name = "admin_dash/user/user_update.html"

    def get_success_url(self):
        return reverse_lazy("user_list_admin")


class UserDeleteView(DeleteView):
    model = User
    pk_url_kwarg = "id"
    template_name = "admin_dash/user/user_delete.html"

    def get_success_url(self):
        return reverse_lazy("user_list_admin")
