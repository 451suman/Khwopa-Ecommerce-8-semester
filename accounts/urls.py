from django.urls import path

from accounts.views import ActivateAccountView, CustomerLoginView, CustomerLogoutView, CustomerSignUpView, UserChangePasswordView, UserProfileUpdateView

urlpatterns = [
    path(
        "customer/login/",
        CustomerLoginView.as_view(),
        name="customer_login",
    ),
    path("customer/signup/", CustomerSignUpView.as_view(), name="customer_signup"),
    path("activate/", ActivateAccountView.as_view(), name="activate_account"),
    path("customer/logout/", CustomerLogoutView.as_view(), name="customer_logout"),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path("password/change/", UserChangePasswordView.as_view(), name="change_password"),

]
