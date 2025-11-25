from django.urls import path

from accounts.accounts_admin.views import AdminLoginView, AdminLogoutView, UserDeleteView, UserListView, UserUpdateView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin_login"),
    path("logout/", AdminLogoutView.as_view(), name="admin_logout"),
    path("admin/users/", UserListView.as_view(), name="user_list_admin"),
    path("admin/users/<int:id>/edit/", UserUpdateView.as_view(), name="user_update_admin"),
    path("admin/users/<int:id>/delete/", UserDeleteView.as_view(), name="user_delete_admin"),

]
