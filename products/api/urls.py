from django.urls import include, path
from rest_framework import routers
from products.api import views

router = routers.DefaultRouter()
# router.register(r"products", views.ProductApiView, basename="products")

urlpatterns = [
    path("", include(router.urls)),
    path("home/", views.HomeApiView.as_view()),
]
