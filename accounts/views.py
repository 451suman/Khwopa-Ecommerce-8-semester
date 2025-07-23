# views.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from accounts.models import CustomUser
from .forms import CustomUserCreationForm, CustomerLoginForm


class WelcomePage(TemplateView):
    template_name = "customer/welcome_page/welcomepage.html"

    # def get(self, request):
    #     return redirect("home")


class CustomerSignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "customer/accounts/signup.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_login")
        return render(request, "customer/accounts/signup.html", {"form": form})


from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import CustomerLoginForm


class CustomerLoginView(FormView):
    template_name = "customer/accounts/login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            form.add_error(None, "Invalid email or password")
            return self.form_invalid(form)

        if not user.check_password(password):
            form.add_error(None, "Invalid email or password")
            return self.form_invalid(form)
        if not user.is_verified:
            form.add_error(None, "Account not verified")
            return self.form_invalid(form)

        if not user.is_active:
            form.add_error(None, "Account is inactive")
            return self.form_invalid(form)

        login(self.request, user)
        return super().form_valid(form)
