from django.urls import path
from . import views

urlpatterns = [
    path('admin_dashboard', views.admin_dashboard_view, name='admin_dashboard'),
    path('sellerverification/<int:id>/',views.seller_verification,name='sellerverification'),
    path('productverification/<int:id>/', views.product_verification, name='productverification'),
    
    # Category/Subcategory Management APIs
    path('api/create-category/', views.create_category, name='create_category'),
    path('api/save-category/', views.save_category, name='save_category'),
    path('api/create-subcategory/', views.create_subcategory, name='create_subcategory'),
    path('api/save-subcategory/', views.save_subcategory, name='save_subcategory'),

    # Attribute Management APIs
    path('api/create-attribute/', views.create_attribute, name='create_attribute'),
    path('api/save-attribute/', views.save_attribute, name='save_attribute'),
    path('api/create-attribute-option/', views.create_attribute_option, name='create_attribute_option'),
    path('api/save-attribute-option/', views.save_attribute_option, name='save_attribute_option'),

    # Category/Subcategory and Banner Management (non-admin namespace to avoid Django admin route conflict)
    path('dashboard/save-category/', views.save_category, name='save_category'),
    path('dashboard/save-subcategory/', views.save_subcategory, name='save_subcategory'),
    path('dashboard/save-banner/', views.save_banner, name='save_banner'),
    path('dashboard/save-variant-bridge/', views.save_variant_attribute_bridge, name='save_variant_attribute_bridge'),
]