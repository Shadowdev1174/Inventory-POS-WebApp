from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    # Point of Sale
    path('', views.POSView.as_view(), name='pos'),
    path('add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update-cart/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove-from-cart/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear-cart/', views.ClearCartView.as_view(), name='clear_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Sales Management
    path('sales/', views.SaleListView.as_view(), name='sale_list'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('receipt/<int:pk>/', views.ReceiptView.as_view(), name='receipt'),
    
    # API endpoints for AJAX
    path('api/search/', views.ProductSearchAPIView.as_view(), name='product_search_api'),
]
