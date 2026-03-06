from django.shortcuts import render,redirect
from core.models import *
from seller.models import *
from core.decorators import admin_required

@admin_required
def admin_dashboard_view(request):
    product_variants=ProductVariant.objects.all()
    seller=SellerProfile.objects.filter(user__role='SELLER')
    context={'products':product_variants,'sellers':seller}
    return render(request,'admin_templates/admindashboard.html',context)

@admin_required
def seller_verification(request, id):
    seller = SellerProfile.objects.get(id=id)
    if request.method == "POST":
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        seller.verification_status = status
        seller.save()
        return redirect('admin_dashboard')
    context = {'seller': seller}
    return render(request, 'admin_templates/seller_verification.html', context)

@admin_required
def product_verification(request, id):
    product = ProductVariant.objects.get(id=id)
    if request.method == "POST":
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        product.approval_status = status
        product.save()
        return redirect('admin_dashboard')
    context = {'product': product}
    return render(request, 'admin_templates/product_verification.html', context)
