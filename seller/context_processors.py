from customer.models import OrderItem


def seller_order_stats(request):
    seller_orders = {
        "seller_total_orders": 0,
        "seller_active_orders": 0,
        "seller_pending_orders": 0,
    }

    user = request.user
    if user.is_authenticated and hasattr(user, "seller_profile"):
        seller = user.seller_profile

        seller_orders["seller_total_orders"] = (
            OrderItem.objects.filter(seller=seller)
            .values("order_id")
            .distinct()
            .count()
        )

        seller_orders["seller_active_orders"] = (
            OrderItem.objects.filter(seller=seller)
            .exclude(status__in=["delivered", "cancelled"])
            .values("order_id")
            .distinct()
            .count()
        )

        seller_orders["seller_pending_orders"] = (
            OrderItem.objects.filter(seller=seller, status__in=["pending", "processing"])
            .values("order_id")
            .distinct()
            .count()
        )

    return seller_orders
