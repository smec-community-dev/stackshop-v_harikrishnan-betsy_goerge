from django.urls import path
from . import views

urlpatterns = [
    path('seller_bridge/', views.seller_bridge, name='seller-bridge'),
    path('sellerprofile',views.seller_profile_view,name='seller-profile')

]
