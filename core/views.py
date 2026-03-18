from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from core.decorators import admin_required, seller_required
from customer.models import Cart, CartItem, WishlistItem
from .models import CustomUser, EmailOTP, Category, Banner
from seller.models import *
from django.db.models import Q, Count
import random


def home_view(request):
    user = request.user
    category_items = Category.objects.all()
    current_time = timezone.now()

    banners = (
        Banner.objects.filter(
            is_active=True,
            start_date__lte=current_time,
            end_date__gte=current_time,
        )
        .order_by("-created_at")
    )

    product_var = (
        ProductVariant.objects.select_related("product__subcategory__category")
        .prefetch_related("images")
        .filter(product__approval_status="approved")
    )

    top_picks = (
        Product.objects.filter(approval_status="approved", is_active=True)
        .annotate(review_count=Count("review"))
        .select_related("subcategory__category")
        .prefetch_related("variants__images")
        .order_by("-review_count", "-created_at")[:12]
    )
    if user.is_authenticated and user.is_admin:
        return redirect(request.META.get("HTTP_REFERER", "admin_dashboard"))
    # if user.is_authenticated and user.role=="SELLER":
    #     return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    wishlist_product_ids = set()
    if user.is_authenticated:
        wishlist_product_ids = set(
            WishlistItem.objects.filter(wishlist__user=user)
            .values_list("variant__product_id", flat=True)
        )

    if user.is_authenticated:
        cart = Cart.objects.filter(user=user).first()
        cart_items = CartItem.objects.filter(cart=cart).prefetch_related(
            "variant__product__subcategory", "variant__images"
        )

        for product in top_picks:
            product.is_in_wishlist = product.id in wishlist_product_ids

        return render(
            request,
            "core_templates/homepage.html",
            {
                "user": user,
                "cart_items": cart_items,
                "categories": category_items,
                "product_var": product_var,
                "top_picks": top_picks,
                "banners": banners,
            },
        )
    return render(
        request,
        "core_templates/homepage.html",
        {
            "categories": category_items,
            "product_var": product_var,
            "top_picks": top_picks,
            "banners": banners,
        },
    )


# search-------------------------------------------------------------------------
def search_and_filter_view(request):
    query = request.GET.get("q", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    selected_categories = request.GET.getlist("category")
    selected_subcategory = request.GET.get("subcategory", "")
    sort_by = request.GET.get("sort", "featured")
    user = request.user

    if query:
        matched_variants = (
            ProductVariant.objects.filter(
                product__approval_status="approved", product__is_active=True
            )
            .filter(
                Q(product__name__icontains=query)
                | Q(product__description__icontains=query)
                | Q(product__subcategory__category__name__icontains=query)
            )
            .distinct()
        )
    elif selected_subcategory:
        matched_variants = ProductVariant.objects.filter(
            product__subcategory__slug=selected_subcategory,
            product__approval_status="approved",
            product__is_active=True,
        ).distinct()
    elif selected_categories:
        matched_variants = ProductVariant.objects.filter(
            product__approval_status="approved", product__is_active=True
        )
    elif min_price or max_price:
        matched_variants = ProductVariant.objects.filter(
            product__approval_status="approved", product__is_active=True
        )
    else:
        matched_variants = ProductVariant.objects.none()

    if selected_categories and "all" not in selected_categories:
        matched_variants = matched_variants.filter(
            product__subcategory__category__slug__in=selected_categories
        ).distinct()

    if min_price:
        try:
            min_price_val = float(min_price)
            matched_variants = matched_variants.filter(selling_price__gte=min_price_val)
        except (ValueError, TypeError):
            pass

    if max_price:
        try:
            max_price_val = float(max_price)
            matched_variants = matched_variants.filter(selling_price__lte=max_price_val)
        except (ValueError, TypeError):
            pass

    if sort_by == "price-low-high":
        matched_variants = matched_variants.order_by("selling_price")
    elif sort_by == "price-high-low":
        matched_variants = matched_variants.order_by("-selling_price")
    elif sort_by == "newest":
        matched_variants = matched_variants.order_by("-created_at")

    product_ids = matched_variants.values_list("product_id", flat=True).distinct()
    product_var = (
        Product.objects.filter(
            id__in=product_ids, approval_status="approved", is_active=True
        )
        .select_related("subcategory__category")
        .prefetch_related("variants__images")
    )

    if selected_categories and "all" not in selected_categories:
        product_var = product_var.filter(
            subcategory__category__slug__in=selected_categories
        ).distinct()

    # Price filtering using annotations since min/max_variant_price are properties (product-level)
    product_var = product_var.annotate(
        min_product_price=models.Min("variants__selling_price"),
        max_product_price=models.Max("variants__selling_price"),
    )

    if min_price:
        try:
            min_price_val = float(min_price)
            product_var = product_var.filter(min_product_price__gte=min_price_val)
        except (ValueError, TypeError):
            pass

    if max_price:
        try:
            max_price_val = float(max_price)
            product_var = product_var.filter(max_product_price__lte=max_price_val)
        except (ValueError, TypeError):
            pass

    # Sorting using annotations since min/max_variant_price are properties (product-level)
    if sort_by == "price-low-high":
        product_var = product_var.annotate(
            min_product_price=models.Min("variants__selling_price")
        ).order_by("min_product_price")
    elif sort_by == "price-high-low":
        product_var = product_var.annotate(
            max_product_price=models.Max("variants__selling_price")
        ).order_by("-max_product_price")
    elif sort_by == "newest":
        product_var = product_var.order_by("-created_at")

    categories = Category.objects.filter(is_active=True)
    wishlist_variant_ids = []
    cart_variant_ids = []
    cart_items = []

    product_wishlist_product_ids = set()
    if user.is_authenticated:
        from customer.models import WishlistItem, Cart, CartItem

        wishlist_variant_ids = list(
            WishlistItem.objects.filter(wishlist__user=user).values_list(
                "variant_id", flat=True
            )
        )
        product_wishlist_product_ids = set(
            WishlistItem.objects.filter(wishlist__user=user).values_list(
                "variant__product_id", flat=True
            )
        )
        cart = Cart.objects.filter(user=user).first()
        if cart:
            cart_items = CartItem.objects.filter(cart=cart).prefetch_related(
                "variant__product__subcategory", "variant__images"
            )
            cart_variant_ids = list(
                CartItem.objects.filter(cart=cart).values_list("variant_id", flat=True)
            )

    # mark wishlist state per product on search/filter results
    for product in product_var:
        product.is_in_wishlist = product.id in product_wishlist_product_ids

    context = {
        "products": product_var,
        "product_var": product_var,
        "search_query": query,
        "cart_items": cart_items,
        "min_price": min_price,
        "max_price": max_price,
        "selected_categories": selected_categories,
        "selected_subcategory": selected_subcategory,
        "sort_by": sort_by,
        "categories": categories,
        "wishlist_variant_ids": wishlist_variant_ids,
        "cart_variant_ids": cart_variant_ids,
    }
    return render(request, "customer_templates/product_page.html", context)


# ------------------------------------------------------------------------------------


def category_list_view(request):
    categories = (
        Category.objects.filter(is_active=True)
        .prefetch_related("subcategories")
        .filter(subcategories__products__approval_status="approved")
        .distinct()
    )
    context = {"categories": categories}
    return render(request, "core_templates/categories.html", context)


def _send_verification_otp(user):
    otp_code = str(random.randint(100000, 999999))
    expiry = timezone.now() + timedelta(minutes=15)
    EmailOTP.objects.create(user=user, otp_code=otp_code, expires_at=expiry)

    subject = "Your StackShop Email Verification OTP"
    message = f"Hello {user.username},\n\nYour verification code is: {otp_code}\nThis code expires in 15 minutes.\n\nThank you for registering with StackShop."
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@stackshop.com")
    send_mail(subject, message, from_email, [user.email], fail_silently=True)


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(
                request,
                "core_templates/registerpage.html",
                {"username": username, "email": email},
            )

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(
                request,
                "core_templates/registerpage.html",
                {"username": username, "email": email},
            )

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(
                request,
                "core_templates/registerpage.html",
                {"username": username, "email": email},
            )

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_verified=False,
        )
        user.save()

        _send_verification_otp(user)
        request.session["pending_verification_user_id"] = user.id
        messages.success(request, "OTP sent to your email. Please verify your account.")
        return redirect("verify_email")

    return render(request, "core_templates/registerpage.html")


def verify_email_view(request):
    pending_user_id = request.session.get("pending_verification_user_id")
    user = None
    if pending_user_id:
        user = CustomUser.objects.filter(id=pending_user_id).first()

    if request.method == "POST":
        otp_code = request.POST.get("otp")
        if not user:
            messages.error(request, "No user pending verification. Please register again.")
            return redirect("register")

        otp_record = (
            EmailOTP.objects.filter(user=user, otp_code=otp_code, is_used=False)
            .filter(expires_at__gte=timezone.now())
            .order_by("-created_at")
            .first()
        )

        if otp_record:
            otp_record.is_used = True
            otp_record.save()
            user.is_verified = True
            user.save()
            request.session.pop("pending_verification_user_id", None)
            messages.success(request, "Email verified successfully. Please login.")
            return redirect("login")

        messages.error(request, "Invalid or expired OTP. Please try again.")

    return render(request, "core_templates/verify_email.html", {"user": user})


def resend_email_otp_view(request):
    pending_user_id = request.session.get("pending_verification_user_id")
    user = None
    if pending_user_id:
        user = CustomUser.objects.filter(id=pending_user_id).first()

    if not user:
        messages.error(request, "No pending verification user found.")
        return redirect("register")

    _send_verification_otp(user)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect("verify_email")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("usernameoremail")
        password = request.POST.get("password")
        try:
            user_obj = CustomUser.objects.get(email=username)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            username = username

        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_verified:
                messages.error(request, "Please verify your email before logging in. Check your inbox for OTP.")
                request.session["pending_verification_user_id"] = user.id
                return redirect("verify_email")

            login(request, user)
            messages.success(request, "User successfully logged in")
            if user.is_admin:
                return redirect("admin_dashboard")
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials !")
    return render(request, "core_templates/loginpage.html")


def logout_view(request):
    logout(request)
    return redirect("home")


def category_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = CartItem.objects.filter(cart=cart).prefetch_related(
        "variant__product__subcategory", "variant__images"
    )
    return render(request, "core_templates/categories.html", {"cart_items": cart_items})


def deals_view(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = CartItem.objects.filter(cart=cart).prefetch_related(
            "variant__product__subcategory", "variant__images"
        )
    else:
        cart_items = []
    return render(request, "core_templates/dealspage.html", {"cart_items": cart_items})


# Create your views here.
