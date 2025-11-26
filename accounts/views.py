# views.py

import random
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from accounts.models import CustomUser
from .forms import CustomUserCreationForm, CustomerLoginForm

from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import CustomerLoginForm

class WelcomePage(TemplateView):
    template_name = "customer/welcome_page/welcomepage.html"

    # def get(self, request):
    #     return redirect("home")


# class CustomerSignUpView(View):
#     def get(self, request):
#         form = CustomUserCreationForm()
#         return render(request, "customer/accounts/signup.html", {"form": form})

#     def post(self, request):
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user =form.save()
#             user.is_verified = True
#             user.save()
#             return redirect("customer_login")
#         return render(request, "customer/accounts/signup.html", {"form": form})

# from django.core.mail import send_mail
# from django.conf import settings
# from django.contrib import messages

# class CustomerSignUpView(View):
#     def get(self, request):
#         form = CustomUserCreationForm()
#         return render(request, "customer/accounts/signup.html", {"form": form})

#     def post(self, request):
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # user.is_verified = True
#             user.otp = random.randint(100000, 999999)
#             user.save()

#             subject = "Welcome to Our Store!"
#             message = f"""
#             Hi {user.full_name},

#             Your account has been created successfully.
#             Thanks for joining us!

#             To activate your account, please click the link below:

#             http://127.0.0.1:8000/accounts/activate/?token={user.otp}


#             Regards,
#             Khwopa Ecommerce
#             """
#             send_mail(
#                 subject,
#                 message,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [user.email],
#                 fail_silently=False,
#             )
#             print("----------------------------------------")
#             print("Email Sent")
#             print("----------------------------------------")
#             return redirect("customer_login")

#         return render(request, "customer/accounts/signup.html", {"form": form})



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


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")



import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from .forms import CustomUserCreationForm
from .models import CustomUser

class CustomerSignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "customer/accounts/signup.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False  # initially unverified
            user.otp = str(uuid.uuid4())  # generate unique activation token
            user.save()

            # Build activation link
            activation_link = request.build_absolute_uri(
                f"/accounts/activate/?token={user.otp}"
            )

            # Send activation email
            subject = "Activate Your Khwopa Ecommerce Account"
            message = f"""
            Hi {user.full_name},

            Thanks for registering at Khwopa Ecommerce!

            Please click the link below to activate your account:

            {activation_link}

            If you did not register, please ignore this email.

            Regards,
            Khwopa Ecommerce Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "Signup successful! Please check your email to activate your account.")
            return redirect("customer_login")

        return render(request, "customer/accounts/signup.html", {"form": form})



from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from .models import CustomUser

class ActivateAccountView(View):
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            messages.error(request, "Invalid activation link.")
            return redirect("customer_login")

        try:
            user = CustomUser.objects.get(otp=token)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid or expired activation token.")
            return redirect("customer_login")

        if user.is_verified:
            messages.info(request, "Your account is already activated. Please login.")
            return redirect("customer_login")

        # Activate the user
        user.is_verified = True
        user.otp = ""  # clear OTP after use
        user.save()

        messages.success(request, "Your account has been activated successfully! You can now login.")
        return redirect("customer_login")
