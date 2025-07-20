from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from accounts.views import WelcomePage
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", WelcomePage.as_view(), name="wellcome-page"),
    path("accounts/", include("accounts.urls")),
    path("vendor/", include("vendor.urls")),
    path("products/", include("products.urls")),
    # api
    path("api/", include("products.api.urls")),  # product api


    # admin url
    path("admin-account/", include("accounts.accounts_admin.urls")),
    path("admin-product/", include("products.products_admin.urls")),

] + debug_toolbar_urls()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
