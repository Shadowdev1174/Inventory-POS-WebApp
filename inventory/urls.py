from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/update-theme/', views.update_theme_preference, name='update_theme_preference'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/archived/', views.ArchivedProductsView.as_view(), name='archived_products'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Bulk operations
    path('products/bulk-archive/', views.bulk_archive_products, name='bulk_archive'),
    path('products/bulk-delete/', views.bulk_delete_products, name='bulk_delete'),
    path('products/export/', views.export_products, name='export_products'),
    path('products/<int:pk>/quick-edit/', views.product_quick_edit, name='product_quick_edit'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
