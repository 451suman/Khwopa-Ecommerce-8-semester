from django.db.models import Sum, Count, Q
from django.db.models.functions import Coalesce
from products.models import Order

def orderstatuscountFunc(request):
    agg = Order.objects.aggregate(
        Received   = Count("id", filter=Q(order_status="Order Received")),
        Processing = Count("id", filter=Q(order_status="Order Processing")),
        way        = Count("id", filter=Q(order_status="On the way")),
        Completed  = Count("id", filter=Q(order_status="Order Completed")),
        Canceled   = Count("id", filter=Q(order_status="Order Canceled")),
        totalincome= Coalesce(Sum("total"), 0),
    )

    # If these come from elsewhere, remove the defaults and plug in the real values.
    agg.setdefault("CustomerCount", 0)
    agg.setdefault("contacts_count_read", 0)
    agg.setdefault("contacts_count_unread", 0)

    return agg
