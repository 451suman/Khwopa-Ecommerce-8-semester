from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts import models
from django.contrib.auth import get_user_model

from products.models import Brand, Category, Color, Order, Product, Review
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
    queryset = Product.objects.select_related("vendor", "category").prefetch_related("product_images", "review_set").all()
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    
    def get_queryset(self):
        queryset =super().get_queryset()
        if self.request.user.is_vendor and hasattr(self.request.user, "vendor"):
            queryset = queryset.filter(vendor=self.request.user.vendor)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = self.object.review_set.all()
        
        context["reviews"] = reviews
        context["review_count"] = reviews.count()
        context["avg_rating"] = round(reviews.aggregate(Avg("rating"))["rating__avg"] or 0)

        # Optional: context["total_orders"] = ... (if needed)
        return context

from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import AdminBrandForm, AdminCategoryForm, AdminColorForm, ProductForm, ProductImageFormSet
from products.models import Product

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = "admin_dash/product_add_update/product_add.html"
    success_url = reverse_lazy("product_list_admin")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = ProductImageFormSet(prefix="product_images")
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES, prefix="product_images")
        if form.is_valid() and formset.is_valid():
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
        form = self.form_class(instance=product)
        formset = ProductImageFormSet(instance=product, prefix="product_images")
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = self.form_class(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix="product_images")
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

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Category created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create category. Please check the form.")
        return super().form_invalid(form)
    
class CategoryAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Category
    form_class = AdminCategoryForm
    template_name = "admin_dash/category/create/category_create.html"
    success_url = reverse_lazy("category_list_admin")
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Category updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update category. Please check the form.")
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

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Brand created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create brand. Please check the form.")
        return super().form_invalid(form)
    

class BrandAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Brand
    form_class = AdminBrandForm
    template_name = "admin_dash/brands/create/create_brand.html"
    success_url = reverse_lazy("brand_list_admin")
    pk_url_kwarg = "id"  # changed from slug to id

    def form_valid(self, form):
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

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Color created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create color. Please check the form.")
        return super().form_invalid(form)

class ColorAdminUpdateView(AdminOrMerchantRequiredMixin, UpdateView):
    model = Color
    form_class = AdminColorForm
    template_name = "admin_dash/colour/create/colour_create.html"
    success_url = reverse_lazy("color_list_admin")
    pk_url_kwarg = "id"  

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Color updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update color. Please check the form.")
        return super().form_invalid(form)    
    
class ColorAdminDeleteView(AdminOrMerchantRequiredMixin, DeleteView):
    model = Color
    success_url = reverse_lazy("color_list_admin")
    pk_url_kwarg = "id"