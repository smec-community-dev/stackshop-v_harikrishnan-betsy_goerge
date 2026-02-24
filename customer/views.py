from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from seller.models import Product,ProductVariant
@login_required
def user_profile_view(request):
    user=request.user
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        phone=request.POST.get('phone')
        image=request.FILES.get('profile_photo')
        user.first_name=first_name
        user.last_name=last_name
        user.phone_number=phone
        if image:
            user.profile_image=image
        user.save()
    return render(request,'customer_templates/profile.html',{"user":user})
def customer_dashboard_view(request):
    return render(request,'customer_templates/customer_dashboard.html')
def product_list_view(request):
    product_var=ProductVariant.objects.all()
    return render(request,'customer_templates/product_page.html',{"product_var":product_var})
# Create your views here.
