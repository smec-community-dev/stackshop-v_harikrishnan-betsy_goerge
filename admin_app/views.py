from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.models import *
from seller.models import *
from core.decorators import admin_required
from .forms import (
    AttributeForm,
    AttributeOptionForm,
    CategoryForm,
    SubCategoryForm,
    BannerForm,
    VariantAttributeBridgeForm,
)


@admin_required
def admin_dashboard_view(request):
    product_variants = ProductVariant.objects.all()
    seller = SellerProfile.objects.filter(user__role="SELLER")
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    attributes = Attribute.objects.all()

    context = {
        "products": product_variants,
        "sellers": seller,
        "categories": categories,
        "subcategories": subcategories,
        "attributes": attributes,
        "attribute_form": AttributeForm(),
        "attribute_option_form": AttributeOptionForm(),
        "category_form": CategoryForm(),
        "subcategory_form": SubCategoryForm(),
        "banner_form": BannerForm(),
        "bridge_form": VariantAttributeBridgeForm(),
    }
    return render(request, "admin_templates/admindashboard.html", context)


@admin_required
def seller_verification(request, id):
    seller = get_object_or_404(SellerProfile, id=id)
    if request.method == "POST":
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")
        seller.verification_status = status
        seller.admin_remarks = remarks

        # Update CustomUser field explicitly
        if status == "approved":
            seller.user.is_verified_seller = True
        else:
            seller.user.is_verified_seller = False
        seller.user.save()
        seller.save()
        messages.success(
            request, f"Seller '{seller.store_name}' {status.upper()} successfully!"
        )
        return redirect("admin_dashboard")
    context = {"seller": seller}
    return render(request, "admin_templates/seller_verification.html", context)


@admin_required
def product_verification(request, id):
    product_variant = get_object_or_404(ProductVariant, id=id)
    product = product_variant.product
    if request.method == "POST":
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")
        product.approval_status = status
        product.admin_remarks = remarks
        product.save()
        return redirect(f"{reverse('admin_dashboard')}#products")
    context = {"product": product}
    return render(request, "admin_templates/product_verification.html", context)


# ==================== ATTRIBUTE MANAGEMENT FORMS ====================


@admin_required
@require_http_methods(["POST"])
def create_attribute(request):
    """Legacy alias for save_attribute."""
    return save_attribute(request)


@admin_required
@require_http_methods(["POST"])
def save_attribute(request):
    """Handle attribute creation or update via regular form submission."""
    attribute_id = request.POST.get("id") or request.POST.get("attribute_id")
    if attribute_id:
        attribute = get_object_or_404(Attribute, id=attribute_id)
        form = AttributeForm(request.POST, instance=attribute)
        action = "updated"
    else:
        form = AttributeForm(request.POST)
        action = "created"

    if form.is_valid():
        attribute = form.save()
        messages.success(request, f"Attribute '{attribute.name}' {action} successfully!")
    else:
        messages.error(request, "Attribute save failed: " + "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()]))

    return redirect("admin_dashboard")


@admin_required
@require_http_methods(["POST"])
def create_category(request):
    """Legacy alias for save_category."""
    return save_category(request)


@admin_required
@require_http_methods(["POST"])
def save_category(request):
    """Handle category creation or update via regular form submission."""
    category_id = request.POST.get("id") or request.POST.get("category_id")

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        form = CategoryForm(request.POST, request.FILES or None, instance=category)
        action = "updated"
    else:
        form = CategoryForm(request.POST, request.FILES or None)
        action = "created"

    if form.is_valid():
        category = form.save()
        messages.success(request, f"Category '{category.name}' {action} successfully!")
    else:
        messages.error(request, "Category save failed: " + "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()]))

    return redirect("admin_dashboard")


@admin_required
@require_http_methods(["POST"])
def create_subcategory(request):
    """Legacy alias for save_subcategory."""
    return save_subcategory(request)


@admin_required
@require_http_methods(["POST"])
def save_subcategory(request):
    """Handle subcategory creation or update via regular form submission."""
    subcategory_id = request.POST.get("id") or request.POST.get("subcategory_id")

    if subcategory_id:
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        form = SubCategoryForm(request.POST, request.FILES or None, instance=subcategory)
        action = "updated"
    else:
        form = SubCategoryForm(request.POST, request.FILES or None)
        action = "created"

    if form.is_valid():
        subcategory = form.save()
        messages.success(request, f"SubCategory '{subcategory.name}' {action} successfully!")
    else:
        messages.error(request, "SubCategory save failed: " + "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()]))

    return redirect("admin_dashboard")


@admin_required
@require_http_methods(["POST"])
def create_attribute_option(request):
    """Legacy alias for save_attribute_option."""
    return save_attribute_option(request)


@admin_required
@require_http_methods(["POST"])
def save_attribute_option(request):
    """Handle attribute option creation or update via regular form submission."""
    option_id = request.POST.get("id") or request.POST.get("attribute_option_id")
    if option_id:
        option = get_object_or_404(AttributeOption, id=option_id)
        form = AttributeOptionForm(request.POST, instance=option)
        action = "updated"
    else:
        form = AttributeOptionForm(request.POST)
        action = "added"

    if form.is_valid():
        option = form.save()
        messages.success(request, f"Option '{option.value}' {action} successfully!")
    else:
        messages.error(request, "Attribute option save failed: " + "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()]))

    return redirect("admin_dashboard")


@admin_required
@require_http_methods(["POST"])
def save_banner(request):
    banner_id = request.POST.get("id") or request.POST.get("banner_id")
    if banner_id:
        banner = get_object_or_404(Banner, id=banner_id)
        form = BannerForm(request.POST, request.FILES or None, instance=banner)
        action = "updated"
    else:
        form = BannerForm(request.POST, request.FILES or None)
        action = "created"

    if form.is_valid():
        b = form.save()
        messages.success(request, f"Banner '{b.title}' {action} successfully!")
    else:
        messages.error(request, "Banner save failed: " + "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()]))

    return redirect("admin_dashboard")


@admin_required
@require_http_methods(["POST"])
def save_variant_attribute_bridge(request):
    bridge_id = request.POST.get("id") or request.POST.get("bridge_id")
    if bridge_id:
        bridge = get_object_or_404(VariantAttributeBridge, id=bridge_id)
        form = VariantAttributeBridgeForm(request.POST, instance=bridge)
        action = "updated"
    else:
        form = VariantAttributeBridgeForm(request.POST)
        action = "created"

    if form.is_valid():
        b = form.save()
        messages.success(request, f"Attribute bridge for variant '{b.variant}' and option '{b.option}' {action} successfully!")
    else:
        messages.error(request, "Attribute bridge save failed: " + "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()]))

    return redirect("admin_dashboard")


# Seller/Product verification is now handled with normal form POST submission via seller_verification and product_verification views
# (No AJAX variant functions are required in this codepath.)
