from django.shortcuts import render,redirect
from core.decorators import seller_required
from django.contrib.auth.decorators import login_required
from .models import SellerProfile

@login_required
def seller_profile_view(request):
    profile, created = SellerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.store_name = request.POST.get("store_name")
        profile.store_slug = request.POST.get("store_slug")
        profile.gst_number = request.POST.get("gst_number")
        profile.pan_number = request.POST.get("pan_number")
        profile.bank_account_number = request.POST.get("bank_account_number")
        profile.ifsc_code = request.POST.get("ifsc_code")
        profile.business_address = request.POST.get("business_address")

        
        if request.FILES.get("store_image"):
            profile.store_image = request.FILES.get("store_image")

        profile.save()
        return redirect('seller-profile')

    return render(request, "seller_templates/sellerprofilepage.html", {"profile": profile})

def seller_bridge(request):
    user=request.user
    if user.is_authenticated:
        if SellerProfile.objects.filter(user=request.user).exists():
            return redirect("seller-profile")

        if request.method == "POST":
            store_name = request.POST.get("store_name")
            gst_number = request.POST.get("gst_number")
            pan_number = request.POST.get("pan_number")
            bank_account_number = request.POST.get("bank_account_number")
            ifsc_code = request.POST.get("ifsc_code")
            business_address = request.POST.get("business_address")
            store_image = request.FILES.get("store_image")
    return render(request, "seller_templates/seller_bridge.html")


# Create your views here.
