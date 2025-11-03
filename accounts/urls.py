from django.urls import path

from accounts.views import CustomerLoginView, CustomerLogoutView, CustomerSignUpView

urlpatterns = [
    path(
        "customer/login/",
        CustomerLoginView.as_view(),
        name="customer_login",
    ),
    path("customer/signup/", CustomerSignUpView.as_view(), name="customer_signup"),
    path("customer/logout/", CustomerLogoutView.as_view(), name="customer_logout"),

]
