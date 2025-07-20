from django.urls import include, path

from products.views import (
    BrandProductListView,
    CategoryProductListView,
    CheckoutView,
    CustomerOrderDetailView,
    EmptyCartView,
    HomeView,
    VendorNamelistView,
    VendorProductListView,
    categoryNamelistView,
    OrderListView,
    ProductDetailView,
    ProductListView,
    MyCartView,
    AddToCartView,
    ManageCartView,
    FilerProductView,
)

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    # product
    path("list/", ProductListView.as_view(), name="product_list"),
    path("detail/<str:slug>/", ProductDetailView.as_view(), name="product_detail"),
    # category product list
    path(
        "category/<str:slug>/",
        CategoryProductListView.as_view(),
        name="category_product_list",
    ),
    path("categoris/", categoryNamelistView.as_view(), name="categoris_name_list"),
    # vendor product list
    path("vendor/", VendorNamelistView.as_view(), name="vendor_name_list"),
    path("vendor/<str:slug>/", VendorProductListView.as_view(), name="vendor_product_list"),

    # Brand product list 
    path("brand/<int:id>/", BrandProductListView.as_view(), name="brand_product_list"),

    # price filer
    path("price-filter/", FilerProductView.as_view(), name="price-filter"),
    # cart
    path("add-to-cart/<int:pk>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/", MyCartView.as_view(), name="my-cart"),
    path("empty-cart/", EmptyCartView.as_view(), name="empty-cart"),
    path("manage-cart/<int:pk>/", ManageCartView.as_view(), name="managecart"),
    # checkout
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    # order
    path("order-list/", OrderListView.as_view(), name="order-list"),
    path("order/<int:pk>/", CustomerOrderDetailView.as_view(), name="order_detail"),
]
