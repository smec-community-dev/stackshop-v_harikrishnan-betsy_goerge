from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('profile/',views.user_profile_view,name='profile'),
    path('customer_dashboard/',views.customer_dashboard_view,name='customer_dashboard'),
    path('products/',views.product_list_view,name='product_list'),
]
