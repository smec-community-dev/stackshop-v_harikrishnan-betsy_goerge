from django.urls import path
from . import views

urlpatterns = [
    path('admin_dashboard', views.admin_dashboard_view, name='admin_dashboard'),
    path('sellerverification/<int:id>/',views.seller_verification,name='sellerverification'),
    path('productverification/<int:id>/', views.product_verification, name='productverification')
]
