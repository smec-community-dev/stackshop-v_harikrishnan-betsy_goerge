from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.models import *
from seller.models import SellerProfile, Product, ProductVariant
from core.decorators import admin_required
from .forms import (
    CategoryForm,
    SubCategoryForm,
    BannerForm,
    DealForm,
)
from .models import Deal


@admin_required
def admin_dashboard_view(request):
    product_variants = ProductVariant.objects.all()
    seller = SellerProfile.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    context = {
        "products": product_variants,
        "sellers": seller,
        "categories": categories,
        "subcategories": subcategories,
        "category_form": CategoryForm(),
        "subcategory_form": SubCategoryForm(),
        "banner_form": BannerForm(),
    }
    return render(request, "admin_templates/admindashboard.html", context)


@admin_required
def add_deal(request):
    edit_id = request.GET.get('edit')
    deal = None
    if edit_id:
        deal = get_object_or_404(Deal, id=edit_id)
    
    if request.method == 'POST':
        form = DealForm(request.POST, request.FILES, instance=deal)
        if form.is_valid():
            form.save()
            if deal:
                messages.success(request, 'Deal updated successfully!')
            else:
                messages.success(request, 'Deal created successfully!')
            return redirect('manage_deals')
        else:
            messages.error(request, 'Error saving deal. Please fix the errors below.')
    else:
        form = DealForm(instance=deal)

    context = {
        'deal_form': form,
        'deal': deal,
        'is_edit': bool(deal),
    }
    return render(request, 'admin_templates/add_deals.html', context)


@admin_required
def edit_deal(request, id):
    deal = get_object_or_404(Deal, id=id)
    
    if request.method == 'POST':
        form = DealForm(request.POST, request.FILES, instance=deal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Deal "{deal.title}" updated successfully!')
            return redirect('manage_deals')
        else:
            messages.error(request, 'Error updating deal. Please fix the errors below.')
    else:
        form = DealForm(instance=deal)

    context = {
        'deal_form': form,
        'deal': deal,
        'is_edit': True,
    }
    return render(request, 'admin_templates/add_deals.html', context)


@admin_required
def manage_deals(request):
    deals = Deal.objects.all().order_by('-created_at')
    context = {
        'deals': deals,
    }
    return render(request, 'admin_templates/manage_deals.html', context)


@admin_required
def delete_deal(request):
    if request.method == 'POST':
        deal_id = request.POST.get('deal_id')
        if deal_id:
            deal = get_object_or_404(Deal, id=deal_id)
            deal_title = deal.title
            deal.delete()
            messages.success(request, f'Deal "{deal_title}" has been deleted successfully!')
        else:
            messages.error(request, 'Invalid deal ID.')
    return redirect('manage_deals')


@admin_required
def seller_verification(request, id):
    seller = get_object_or_404(SellerProfile, id=id)
    if request.method == "POST":
        status = request.POST.get("status")
        remarks = request.POST.get("remarks")
        seller.verification_status = status
        seller.admin_remarks = remarks

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
    # now operate on Product directly (id is product id)
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        status = (request.POST.get("status") or "").strip().lower()
        if status not in ["pending", "approved", "rejected"]:
            messages.error(request, "Invalid status value. Please choose pending, approved, or rejected.")
            return redirect(request.path)

        remarks = request.POST.get("remarks", "").strip()
        product.approval_status = status
        product.admin_remarks = remarks
        product.save()
        messages.success(request, f"Product '{product.name}' status updated to {status}.")
        return redirect(f"{reverse('admin_dashboard')}#products")
    context = {"product": product}
    return render(request, "admin_templates/product_verification.html", context)


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




# Seller/Product verification is now handled with normal form POST submission via seller_verification and product_verification views
# (No AJAX variant functions are required in this codepath.)
