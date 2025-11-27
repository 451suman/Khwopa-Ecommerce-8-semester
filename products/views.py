from multiprocessing import Value
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
from django.db.models.functions import Coalesce
from django.db.models import Q
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
        # new_products = cache.get("new_products")
        # if not new_products:
        new_products = (
            Product.objects.prefetch_related("product_images")
            .annotate(average_rating=Avg("review__rating"))
            .order_by("-created_at")[:5]
        )
        # cache.set("new_products", new_products, 60)
        return new_products


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Annotate products with average rating
        product_qs = Product.objects.prefetch_related("product_images").annotate(
            average_rating=Avg("review__rating")
        )

        # Top 5 rated products
        # Top 5 rated products with reviews
        top_rated = product_qs.filter(average_rating__isnull=False).order_by("-average_rating")[:5]


        # Categories
        categories = (
            Category.objects.prefetch_related(Prefetch("products", queryset=product_qs))
            .filter(arranged__isnull=False)
            .order_by("arranged")
        )

        context["categories"] = categories
        context["top_rated"] = top_rated  # <-- add this
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


def brands_list_func(request):
    brands = Brand.objects.all()
    return brands


from django.shortcuts import render
from django.views.generic import ListView
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = "customer/product/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        # Fetch products with prefetch_related to optimize image loading
        qs = Product.objects.prefetch_related("product_images")

        # Get the 'sort' parameter from the GET request
        sort = self.request.GET.get("sort")
        search = self.request.GET.get("search")

        # If the user wants to sort low-to-high or high-to-low, we apply sorting in Python
        if sort == "low_to_high":
            # Bubble Sort to sort by 'current_price' in ascending order
            products = list(qs)  # Convert queryset to list to apply sorting
            for i in range(len(products) - 1):
                for j in range(len(products) - 1 - i):
                    if products[j].current_price > products[j + 1].current_price:
                        # products[j], products[j + 1] = products[j + 1], products[j]
                        temp = products[j]            # Store current product temporarily
                        products[j] = products[j + 1] # Move the next product to current position
                        products[j + 1] = temp        # Move the stored product to the next position
            qs = products

        elif sort == "high_to_low":
            # Bubble Sort to sort by 'current_price' in descending order
            products = list(qs)  # Convert queryset to list to apply sorting
            for i in range(len(products) - 1):
                for j in range(len(products) - 1 - i):
                    if products[j].current_price < products[j + 1].current_price:
                        # products[j], products[j + 1] = products[j + 1], products[j]
                        temp = products[j]            # Store current product temporarily
                        products[j] = products[j + 1] # Move the next product to current position
                        products[j + 1] = temp        # Move the stored product to the next position
            qs = products

        # Default sorting by 'created_at' in descending order
        else:
            qs = qs.order_by("-created_at")

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        context["related_products"] = product.get_similar_products()

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
        context["average_rating"] = round(average_rating)

        # Check if user can review
        can_review = False
        if user.is_authenticated:
            has_completed_order = Order.objects.filter(
                user=user,
                order_status="Order Completed",
                cart_products__product=product,
            ).exists()

            has_reviewed = reviews_qs.filter(user=user).exists()

            can_review = has_completed_order and not has_reviewed 

        context["can_review"] = can_review
        context["has_reviewed"] = has_reviewed
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


from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin


class CheckoutView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "customer/checkout/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id")
        cart_obj = None
        if cart_id:
            try:
                cart_obj = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart_obj = None
        context["cart"] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if not cart_id:
            messages.error(
                self.request,
                "No active cart found. Please add items to your cart first.",
            )
            return redirect("home")

        try:
            cart_obj = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            messages.error(self.request, "Cart not found. Please try again.")
            return redirect("home")

        # Check if an order already exists for this cart
        if Order.objects.filter(cart=cart_obj).exists():
            messages.warning(
                self.request, "An order has already been placed for this cart."
            )
            return redirect(self.success_url)

        # Set form fields before saving
        form.instance.user = self.request.user
        form.instance.cart = cart_obj
        form.instance.subtotal = cart_obj.total
        form.instance.discount = 0
        form.instance.total = cart_obj.total
        form.instance.order_status = "Order Received"
        order = form.save()

        # Create vendor order items
        # cart_items = cart_obj.cartproduct_set.all()
        # for item in cart_items:
        #     vendor_items = VendorOrderItem.objects.create(
        #         order=form.instance,
        #         vendor=item.product.vendor,
        #         product=item.product,
        #         rate=item.rate,
        #         quantity=item.quantity,
        #         subtotal=item.subtotal,
        #     )

        # Clear cart_id from session
        del self.request.session["cart_id"]

        response = super().form_valid(form)  # This saves the order

        messages.success(self.request, "Your order has been received successfully!")

        return response


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


from django.shortcuts import get_object_or_404
from django.http import Http404


class CategoryProductListView(EcomMixin, ListView):
    model = Product
    template_name = "customer/product/product_list.html"
    context_object_name = "products"
    paginate_by = 10  # You can change this to the desired number of products per page

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs["slug"])

        return Product.objects.filter(category=category, is_active=True)

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





from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View

class AddReviewView(View):
    def post(self, request, slug):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit a review.")
            return redirect("customer_login")

        product = get_object_or_404(Product, slug=slug)

        # Double check: user must have purchased & order completed
        has_completed_order = Order.objects.filter(
            user=request.user,
            order_status="Order Completed",
            cart_products__product=product,
        ).exists()

        if not has_completed_order:
            messages.error(request, "You cannot review without purchasing this product.")
            return redirect("product_detail", slug=slug)

        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "")

        if Review.objects.filter(product=product, user=request.user).exists():
            messages.info(request, "You already reviewed this product.")
            return redirect("product_detail", slug=slug)

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment,
        )

        messages.success(request, "Your review has been submitted successfully!")
        return redirect("product_detail", slug=slug)
