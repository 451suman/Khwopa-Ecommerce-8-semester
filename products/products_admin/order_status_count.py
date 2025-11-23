from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce
from products.models import CartProduct, Order


def orderstatuscountFunc(request):

    # Prevent errors for anonymous users
    if not request.user.is_authenticated:
        return {}

    if request.user.is_superuser or request.user.is_staff:
        agg = Order.objects.aggregate(
            Received=Count("id", filter=Q(order_status="Order Received")),
            Processing=Count("id", filter=Q(order_status="Order Processing")),
            way=Count("id", filter=Q(order_status="On the way")),
            Completed=Count("id", filter=Q(order_status="Order Completed")),
            Canceled=Count("id", filter=Q(order_status="Order Canceled")),
            totalincome=Coalesce(Sum("total"), 0),
        )

        agg.setdefault("CustomerCount", 0)
        agg.setdefault("contacts_count_read", 0)
        agg.setdefault("contacts_count_unread", 0)

        return agg

    return {}


def VendororderstatuscountFunc(request):

    # FIX: first check authentication
    if not request.user.is_authenticated:
        return {}

    # FIX: safely check is_vendor attribute
    if not getattr(request.user, "is_vendor", False):
        return {}

    # FIX: check .vendor relationship safely
    if not hasattr(request.user, "vendor") or not request.user.vendor:
        return {}

    # If all checks pass → vendor exists → run query
    vendor = request.user.vendor

    agg = CartProduct.objects.filter(vendor=vendor).aggregate(
        Vendor_Order_Received=Count(
            "id", filter=Q(vendor_order_status="Order Received")
        ),
        Vendor_Order_Processing=Count(
            "id", filter=Q(vendor_order_status="Order Processing")
        ),
        Vendor_Order_way=Count(
            "id", filter=Q(vendor_order_status="On the way")
        ),
        Vendor_Order_Completed=Count(
            "id", filter=Q(vendor_order_status="Order Completed")
        ),
        Vendor_Order_Canceled=Count(
            "id", filter=Q(vendor_order_status="Order Canceled")
        ),
        totalincome=Coalesce(Sum("subtotal"), 0),
    )

    agg.setdefault("CustomerCount", 0)
    agg.setdefault("contacts_count_read", 0)
    agg.setdefault("contacts_count_unread", 0)

    return agg
