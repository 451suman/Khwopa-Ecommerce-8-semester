from django.core.cache import cache
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Prefetch
from django.shortcuts import redirect, render, get_object_or_404

from accounts.models import CustomUser
from products.forms import CheckoutForm
from vendor.models import Vendor
from .models import Brand, Cart, CartProduct, Order, Product, Category, Review
from django.contrib import messages


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
                if request.user.is_authenticated:
                    cart_obj.user = (
                        request.user
                    )  # or cart_obj.customer if that's your field
                    cart_obj.save()
            except Cart.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)


from django.db.models import Avg, Prefetch


class HomeView(ListView):
    template_name = "customer/home/home.html"
    model = Product
    context_object_name = "new_products"

    def get_queryset(self):
        new_products = cache.get("new_products")
        if not new_products:
            new_products = (
                Product.objects.prefetch_related("product_images")
                .annotate(average_rating=Avg("review__rating"))
                .order_by("-created_at")[:5]
            )
            # cache.set("new_products", new_products, 60)
        return new_products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cache categories with annotated product ratings
        categories = cache.get("categories")
        if not categories:
            product_qs = Product.objects.prefetch_related("product_images").annotate(
                average_rating=Avg("review__rating")
            )
            categories = (
                Category.objects.prefetch_related(
                    Prefetch("products", queryset=product_qs)
                )
                .filter(arranged__isnull=False)
                .order_by("arranged")
            )
            # cache.set("categories", categories, 60)

        context["categories"] = categories

        top_rated = (
            Product.objects.prefetch_related("product_images")
            .annotate(average_rating=Avg("review__rating"))
            .order_by("-average_rating")[:9]
        )

        context["top_rated"] = top_rated

        return context


# Query 1: Get latest 5 Product objects
# Query 2: Get product_images for those 5 products
# Let’s say 5 categories are returned. Django will:
# Query 3: Get Category objects
# Query 4: Get related Product objects (for those categories)
# Query 5: Get product_images for products in those categories
# Query 6: Session query (django_session)
# Query 7: Auth user query (accounts_customuser)


from django.views.generic import ListView
from .models import Product, Category


def category_list_func(request):
    categories = Category.objects.all()
    return categories


def vendor_list_func(request):
    vendors = Vendor.objects.filter(is_authorized=True).order_by("arranged")
    return vendors


def brands_list_func (request):
    brands = Brand.objects.all()
    return brands

class ProductListView(ListView):
    model = Product
    template_name = "customer/product/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        # Prefetch related product_images and order by created_at descending
        return Product.objects.prefetch_related("product_images").order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add categories to the context
        context["categories"] = category_list_func(self.request)
        context["vendors"] = vendor_list_func(self.request)
        context["brands"] = brands_list_func(self.request)
        return context


# class ProductDetailView(View):
#     def get(self, request, slug):
#         product = get_object_or_404(
#             Product.objects.prefetch_related("product_images"),
#             slug=slug,
#             is_active=True,
#         )

#         return render(
#             request,
#             "customer/product_details/product_details.html",
#             {"product": product},
#         )
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Avg, Prefetch


class ProductDetailView(TemplateView):
    template_name = "customer/product_details/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs["slug"]
        user = self.request.user

        # Optimize product fetch with related objects to avoid extra queries in template
        product = get_object_or_404(
            Product.objects.select_related(
                "category", "brand", "color", "vendor"
            ).prefetch_related("tag", "sizes", "product_images"),
            slug=slug,
        )
        context["product"] = product

        context["related_products"] = product.category.products.exclude(
            id=product.id
        ).order_by("-created_at")

        # Prefetch reviews with user info to avoid query in template
        reviews_qs = Review.objects.filter(product=product).select_related("user")

        context["reviewcount"] = reviews_qs.count()
        context["all_review"] = reviews_qs

        # Average rating with a single aggregate query
        # average_rating = reviews_qs.aggregate(avg=Avg("rating"))["avg"]
        # context["average_rating"] = round(average_rating) if average_rating else 0

        total_rating = 0
        count = 0

        for review in reviews_qs:
            total_rating += review.rating
            count += 1
        if count:
            average_rating = total_rating / count
        else:
            average_rating = 0
        context["average_rating"] = round(average_rating, 2)

        can_review = False
        if user.is_authenticated:
            # Check if user has completed an order with the product
            has_completed_order = Order.objects.filter(
                user=user,
                order_status="Order Completed",
                cart__cartproduct__product=product,
            ).exists()

            # Check if user already reviewed the product
            has_reviewed = reviews_qs.filter(user=user).exists()

            can_review = has_completed_order and not has_reviewed

        context["can_review"] = can_review
        return context


from django.views import View
from django.shortcuts import redirect, get_object_or_404
from .models import Cart, CartProduct, Product


class AddToCartView(EcomMixin, View):
    def get(self, request, pk):
        # Get product or return 404 if not found
        product_obj = get_object_or_404(Product, id=pk)

        # Get cart ID from session
        cart_id = request.session.get("cart_id", None)
        cart_obj = None

        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart_obj = None

        # If cart does not exist, create a new one and save in session
        if not cart_obj:
            cart_obj = Cart.objects.create(total=0)
            request.session["cart_id"] = cart_obj.id

        # Check if product is already in cart
        this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

        if this_product_in_cart.exists():
            cartproduct = this_product_in_cart.last()
            cartproduct.quantity += 1
            cartproduct.subtotal += product_obj.current_price
            cartproduct.save()
        else:
            cartproduct = CartProduct.objects.create(
                cart=cart_obj,
                product=product_obj,
                rate=product_obj.current_price,
                quantity=1,
                subtotal=product_obj.current_price,
            )

        # Update cart total
        # (better to sum subtotals in case of changes)
        cart_obj.total = sum(cp.subtotal for cp in cart_obj.cartproduct_set.all())
        cart_obj.save()

        return redirect("my-cart")


from django.views.generic import TemplateView
from .models import Cart, CartProduct  # make sure to import your models


class MyCartView(EcomMixin, TemplateView):
    template_name = "customer/cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")

        cart = None
        cart_products = []

        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                # Fetch cart products related to this cart
                cart_products = CartProduct.objects.filter(cart=cart)
            except Cart.DoesNotExist:
                cart = None

        context["cart"] = cart
        context["cart_products"] = cart_products
        return context


from django.shortcuts import redirect, get_object_or_404
from django.views import View


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                # Delete all related CartProduct items
                cart.cartproduct_set.all().delete()
                cart.total = 0
                cart.save()
                # Optionally clear cart_id from session
                del request.session["cart_id"]
            except Cart.DoesNotExist:
                # Cart not found, just pass or log
                pass
        return redirect("my-cart")


class ManageCartView(EcomMixin, View):
    def get(self, request, pk):
        print("this is manage cart section")
        # cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=pk)
        cart_obj = cp_obj.cart
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            # delete cartproduct products
            cp_obj.delete()

        else:
            pass

        # print (cp_id, action)
        return redirect("my-cart")


from django.urls import reverse_lazy


class CheckoutView(LoginRequiredMixin, CreateView):
    model = Order  # Define the model here
    template_name = "customer/checkout/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None

        context["cart"] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)

            # Check if an order already exists for this cart
            existing_order = Order.objects.filter(cart=cart_obj).first()
            if existing_order:
                messages.warning(
                    self.request, "An order has already been placed for this cart."
                )
                return redirect(self.success_url)
            form.instance.user = self.request.user
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            

            # Clear cart_id from session
            del self.request.session["cart_id"]

            messages.success(self.request, "Order has been received")
        else:
            return redirect("home")

        return super().form_valid(form)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "customer/order/orderlist/orderlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders"] = Order.objects.filter(user=self.request.user)
        return context


class CustomerOrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "customer/order/orderdetail/customerorderdetail.html"
    context_object_name = "ord_obj"


class CategoryProductListView(EcomMixin, ListView):
    model = Product
    template_name = "customer/product/product_list.html"
    context_object_name = "products"
    paginate_by = 1

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = category_list_func(self.request)
        context["vendors"] = vendor_list_func(self.request)
        context["brands"] = brands_list_func(self.request)

        return context


from django.views.generic import ListView
from .models import Category


class categoryNamelistView(ListView):
    model = Category
    template_name = "customer/names_list/categoriesnamelist.html"
    context_object_name = "names"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


class FilerProductView(View):
    def get(self, request):
        min = request.GET.get("min")
        max = request.GET.get("max")

        product_filter = Product.objects.filter(current_price__range=(min, max))
        categories = category_list_func(self.request)
        vendors = vendor_list_func(self.request)
        return render(
            request,
            "customer/product/product_list.html",
            {"products": product_filter, "categories": categories, "vendors": vendors},
        )


class VendorNamelistView(ListView):
    model = Vendor
    template_name = "customer/names_list/vendorNameList.html"
    context_object_name = "vendors"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Vendors"
        return context


class VendorProductListView(ListView):
    model = Product
    template_name = "customer/product/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        vendor_slug = self.kwargs.get("slug")
        return Product.objects.filter(vendor__slug=vendor_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = category_list_func(self.request)
        context["vendors"] = vendor_list_func(self.request)
        context["brands"] = brands_list_func(self.request)

        return context





class BrandProductListView(ListView):
    model = Product
    template_name = "customer/product/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        brand_id = self.kwargs.get("id")
        return Product.objects.filter(brand__id=brand_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = category_list_func(self.request)
        context["vendors"] = vendor_list_func(self.request)
        context["brands"] = brands_list_func(self.request)

        return context


