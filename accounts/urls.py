from django.urls import path

from accounts.views import CustomerLoginView, CustomerSignUpView

urlpatterns = [
    path(
        "customer/login/",
        CustomerLoginView.as_view(),
        name="customer_login",
    ),
    path("customer/signup/", CustomerSignUpView.as_view(), name="customer_signup"),
]
