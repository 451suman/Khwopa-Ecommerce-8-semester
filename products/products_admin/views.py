from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views import View

from accounts import models
from django.contrib.auth import get_user_model

from products.models import ORDER_STATUS, Brand, CartProduct, Category, Color, Order, Product, ProductImage, Review, Size, Tag
from products.products_admin.forms import ProductForm

User = get_user_model()


class AdminOrMerchantRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (
            models.CustomUser.objects.get(email=request.user.email).is_vendor
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(
                request, "You must be an admin, vendor, or staff to access this page."
            )
            return redirect("admin_login")


from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from products.models import Review, Order
from accounts.models import CustomUser

User = get_user_model()


class DashboardView(AdminOrMerchantRequiredMixin, TemplateView):
    template_name = "admin_dash/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_superuser or user.is_staff:
            # Admin: show everything
            context["user_count"] = User.objects.count()
            context["recent_reviews"] = (
                Review.objects.select_related("user", "product")
                .prefetch_related("product__product_images")
                .order_by("-created_at")[:6]
            )
            context["orders"] = Order.objects.select_related("user").all()
            context["new_orders"] = context["orders"].filter(
                order_status="Order Received"
            )

        elif hasattr(user, "vendor") and user.is_vendor:
            # Vendor: show vendor-specific data
            vendor = user.vendor
            context["user_count"] = User.objects.filter(
                vendor=vendor
            ).count()  # optional, depends on use case

            context["recent_reviews"] = (
                Review.objects.select_related("user", "product")
                .filter(product__vendor=vendor)
                .prefetch_related("product__product_images")
                .order_by("-created_at")[:6]
            )

            context["orders"] = (
                Order.objects.filter(cart__cartproduct__product__vendor=vendor)
                .select_related("user")
                .distinct()
            )

            context["new_orders"] = context["orders"].filter(
                order_status="Order Received"
            )

        else:
            # Should not occur due to AdminRequiredMixin
            context["user_count"] = 0
            context["recent_reviews"] = []
            context["orders"] = []
            context["new_orders"] = []

        return context


# views.py
from django.views.generic import ListView
from products.models import Product
from django.db.models import Prefetch, Avg, Count, Q


class ProductListView(AdminOrMerchantRequiredMixin, ListView):
    model = Product
    template_name = "admin_dash/productlist/productlist.html"
    context_object_name = "products"
    paginate_by = 5

    def get_queryset(self):
        queryset = Product.objects.prefetch_related("product_images", "review_set")
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = queryset

        elif hasattr(user, "vendor") and user.vendor:
            queryset = queryset.filter(vendor=user.vendor)
        else:
            return Product.objects.none()

        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset.annotate(
            avg_rating=Avg("review__rating"), review_count=Count("review")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        return context


class AdminProductDetails(AdminOrMerchantRequiredMixin, DetailView):
    template_name = "admin_dash/product_detail/product_detail.html"
    queryset = (
        Product.objects.select_related("vendor", "category")
        .prefetch_related("product_images", "review_set")
        .all()
    )
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = self.object.review_set.all()

        context["reviews"] = reviews
        context["review_count"] = reviews.count()
        context["avg_rating"] = round(
            reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        )

        # Optional: context["total_orders"] = ... (if needed)
        return context


from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import (
    AdminBrandForm,
    AdminCategoryForm,
    AdminColorForm,
    AdminSizeForm,
    AdminTagForm,
    ProductForm,
    ProductImageFormSet,
)
from products.models import Product


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "admin_dash/product_add_update/product_add.html"
    success_url = reverse_lazy("product_list_admin")

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)
        formset = ProductImageFormSet(prefix="product_images")
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, user=request.user)
        formset = ProductImageFormSet(
            request.POST, request.FILES, prefix="product_images"
        )
        if form.is_valid() and formset.is_valid():
            if self.request.user.is_vendor:
                form.instance.vendor = self.request.user.vendor
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, "Product created successfully!")
            return redirect(self.success_url)
        else:
            messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form, "formset": formset})


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "admin_dash/product_add_update/product_add.html"
    success_url = reverse_lazy("product_list_admin")

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        form = self.form_class(instance=product, user=request.user)
        formset = ProductImageFormSet(instance=product, prefix="product_images")
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = self.form_class(request.POST, instance=product, user=request.user)
        formset = ProductImageFormSet(
            request.POST, request.FILES, instance=product, prefix="product_images"
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Product updated successfully!")
            return redirect(self.success_url)
        else:
            messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"form": form, "formset": formset})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "admin_dash/product_add_update/product_confirm_delete.html"
    success_url = reverse_lazy("product_list_admin")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Product deleted successfully!")
        return super().delete(request, *args, **kwargs)


class CategoryAdminListView(AdminOrMerchantRequiredMixin, ListView):
    queryset = Category.objects.all().order_by("-arranged")
    template_name = "admin_dash/category/list/category_list.html"
    context_object_name = "categories"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_categories"] = Category.objects.count()
        return context


class CategoryAdminCreateView(AdminOrMerchantRequiredMixin, CreateView):
    model = Category
    form_class = AdminCategoryForm
    template_name = "admin_dash/category/create/category_create.html"
    success_url = reverse_lazy("category_list_admin")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Category created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Failed to create category. Please check the form."
        )
        return super().form_invalid(form)


class CategoryAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Category
    form_class = AdminCategoryForm
    template_name = "admin_dash/category/create/category_create.html"
    success_url = reverse_lazy("category_list_admin")
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Failed to update category. Please check the form."
        )
        return super().form_invalid(form)


class CategoryAdminDeleteView(AdminOrMerchantRequiredMixin, DeleteView):
    model = Category
    template_name = "admin_dash/category/delete/category_delete.html"
    success_url = reverse_lazy("category_list_admin")
    slug_field = "slug"
    slug_url_kwarg = "slug"


class BrandAdminListView(AdminOrMerchantRequiredMixin, ListView):
    queryset = Brand.objects.all()
    template_name = "admin_dash/brands/list/brand_list.html"
    context_object_name = "brands"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset


class BrandAdminCreateView(AdminOrMerchantRequiredMixin, CreateView):
    model = Brand
    form_class = AdminBrandForm
    template_name = "admin_dash/brands/create/create_brand.html"
    success_url = reverse_lazy("brand_list_admin")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Brand created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create brand. Please check the form.")
        return super().form_invalid(form)


class BrandAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Brand
    form_class = AdminBrandForm
    template_name = "admin_dash/brands/create/create_brand.html"
    success_url = reverse_lazy("brand_list_admin")
    pk_url_kwarg = "id"  # changed from slug to id

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Brand updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update brand. Please check the form.")
        return super().form_invalid(form)


class BrandADminDeleteView(AdminOrMerchantRequiredMixin, DeleteView):
    model = Brand
    template_name = "admin_dash/brands/delete/delete_brand.html"
    success_url = reverse_lazy("brand_list_admin")
    pk_url_kwarg = "id"  # changed from slug to id

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Brand deleted successfully.")
        return super().delete(request, *args, **kwargs)


class ColorAdminListView(AdminOrMerchantRequiredMixin, ListView):
    queryset = Color.objects.all()
    template_name = "admin_dash/colour/list/colour_list.html"
    context_object_name = "objs"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset


class ColourAdminCreateView(AdminOrMerchantRequiredMixin, CreateView):
    model = Color
    form_class = AdminColorForm
    template_name = "admin_dash/colour/create/colour_create.html"
    success_url = reverse_lazy("color_list_admin")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Color created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create color. Please check the form.")
        return super().form_invalid(form)


class ColorAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Color
    form_class = AdminColorForm
    template_name = "admin_dash/colour/create/colour_create.html"
    success_url = reverse_lazy("color_list_admin")
    pk_url_kwarg = "id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor and not form.instance.vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Color updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update color. Please check the form.")
        return super().form_invalid(form)


class ColorAdminDeleteView(AdminOrMerchantRequiredMixin, DeleteView):
    model = Color
    success_url = reverse_lazy("color_list_admin")
    pk_url_kwarg = "id"


# -----------------------------


class SizeAdminListView(AdminOrMerchantRequiredMixin, ListView):
    queryset = Size.objects.all()
    template_name = "admin_dash/size/list/list.html"
    context_object_name = "objs"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset


class SizeAdminCreateView(AdminOrMerchantRequiredMixin, CreateView):
    model = Size
    form_class = AdminSizeForm
    template_name = "admin_dash/size/create/createform.html"
    success_url = reverse_lazy("size_list_admin")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        response = super().form_valid(form)
        messages.success(self.request, "Color created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create color. Please check the form.")
        return super().form_invalid(form)


class SizeAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Size
    form_class = AdminSizeForm
    template_name = "admin_dash/size/create/createform.html"
    success_url = reverse_lazy("size_list_admin")
    pk_url_kwarg = "id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        messages.success(self.request, "Size updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update Size. Please check the form.")
        return super().form_invalid(form)


class SizeAdminDeleteView(AdminOrMerchantRequiredMixin, DeleteView):
    model = Size
    success_url = reverse_lazy("size_list_admin")
    pk_url_kwarg = "id"


# ---------------------
# for tag i use same tamplets of size because same fields


class TagAdminListView(AdminOrMerchantRequiredMixin, ListView):
    queryset = Tag.objects.all()
    template_name = "admin_dash/tags/list/list.html"
    context_object_name = "objs"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset


class TagAdminCreateView(AdminOrMerchantRequiredMixin, CreateView):
    model = Tag
    form_class = AdminTagForm
    template_name = "admin_dash/tags/create/createform.html"
    success_url = reverse_lazy("tag_list_admin")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        response = super().form_valid(form)
        messages.success(self.request, "Color created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create color. Please check the form.")
        return super().form_invalid(form)


class TagAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Tag
    form_class = AdminTagForm
    template_name = "admin_dash/tags/create/createform.html"
    success_url = reverse_lazy("tag_list_admin")
    pk_url_kwarg = "id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass user to the form
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_vendor:
            form.instance.vendor = self.request.user.vendor
        response = super().form_valid(form)
        messages.success(self.request, "Size updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update Size. Please check the form.")
        return super().form_invalid(form)


class TagAdminDeleteView(AdminOrMerchantRequiredMixin, DeleteView):
    model = Tag
    success_url = reverse_lazy("tag_list_admin")
    pk_url_kwarg = "id"






# order 
class AdminOrderReceivedView(AdminOrMerchantRequiredMixin, ListView):
    model = Order
    template_name = "admin_dash/orders/order_list/order.html"
    paginate_by = 50
    context_object_name = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Received"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").filter(order_status="Order Received").order_by("-id")
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset
class AdminOrderProcessingView(AdminOrMerchantRequiredMixin, ListView):
    model = Order
    template_name = "admin_dash/orders/order_list/order.html"
    paginate_by = 50
    context_object_name = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Processing"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").filter(order_status="Order Processing").order_by("-id")
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor.id)
        return queryset
class AdminOrderOnTheWayView(AdminOrMerchantRequiredMixin, ListView):
    model = Order
    template_name = "admin_dash/orders/order_list/order.html"
    paginate_by = 50
    context_object_name = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "On The Way"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").filter(order_status="On the way").order_by("-id")
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset
class AdminOrderCompletedView(AdminOrMerchantRequiredMixin, ListView):
    model = Order
    template_name = "admin_dash/orders/order_list/order.html"
    paginate_by = 50
    context_object_name = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Completed"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").filter(order_status="Order Completed").order_by("-id")
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset
class AdminOrderCanceledView(AdminOrMerchantRequiredMixin, ListView):
    model = Order
    template_name = "admin_dash/orders/order_list/order.html"
    paginate_by = 50
    context_object_name = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Canceled"
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user").filter(order_status="Order Canceled").order_by("-id")
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset

class AdminOrderDetailView(DetailView):
    model = Order
    template_name = "admin_dash/orders/orders_details/orderdetails.html"
    context_object_name = "order"

    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        cart_items_qs = (
            CartProduct.objects
            .select_related(
                "product",
                "product__brand",
                "product__color",
            )
            .prefetch_related(
                "product__sizes",
                Prefetch(
                    "product__product_images",
                    queryset=ProductImage.objects.order_by("id"),
                    to_attr="_images",  # in-memory list
                )
            )
        )
        return (
            Order.objects
            .select_related("user")
            .prefetch_related(Prefetch("cart_products", queryset=cart_items_qs))
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["allstatus"] = ORDER_STATUS
        return ctx




from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

@require_POST
def admin_change_order_status(request, pk: int):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get("order_status", "").strip()

    valid_choices = dict(ORDER_STATUS)  # e.g. [('PENDING','Pending'), ...]
    if new_status in valid_choices:
        if new_status != order.order_status:
            order.order_status = new_status
            order.save(update_fields=["order_status"])
            messages.success(request, f"Order status updated to {valid_choices[new_status]}.")
        else:
            messages.info(request, "Order status is unchanged.")
    else:
        messages.error(request, "Invalid status selection.")

    # go back to details page (or referrer if you prefer)
    return redirect("admin_order_details", order_number=order.order_number)



