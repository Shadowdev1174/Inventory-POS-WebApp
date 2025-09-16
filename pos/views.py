from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from decimal import Decimal
import json
from datetime import datetime, date
from inventory.models import Product, StockMovement, Category
from .models import Sale, SaleItem, Cart


class POSView(LoginRequiredMixin, TemplateView):
    template_name = 'pos/pos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimized queries with select_related and prefetch_related
        context['cart_items'] = Cart.objects.filter(user=self.request.user).select_related('product__category')
        context['products'] = Product.objects.filter(
            is_active=True, 
            stock_quantity__gt=0
        ).select_related('category').order_by('name')[:20]
        context['categories'] = Category.objects.all().order_by('name')
        
        # Calculate cart totals efficiently
        cart_items = context['cart_items']
        cart_total = sum(item.quantity * item.product.selling_price for item in cart_items)
        cart_count = sum(item.quantity for item in cart_items)
        
        context['cart_total'] = cart_total
        context['cart_count'] = cart_count
        context['cart_tax'] = cart_total * Decimal('0.1')  # 10% tax
        context['cart_final_total'] = cart_total + context['cart_tax']
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class AddToCartView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            if product.stock_quantity < quantity:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Insufficient stock. Only {product.stock_quantity} available.'
                })
            
            # Get or create cart item
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                new_quantity = cart_item.quantity + quantity
                if product.stock_quantity < new_quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Insufficient stock. Only {product.stock_quantity} available.'
                    })
                cart_item.quantity = new_quantity
                cart_item.save()
            
            # Calculate new cart totals
            cart_items = Cart.objects.filter(user=request.user).select_related('product')
            cart_total = sum(item.quantity * item.product.selling_price for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)
            cart_tax = cart_total * Decimal('0.1')
            cart_final_total = cart_total + cart_tax
            
            return JsonResponse({
                'status': 'success',
                'message': f'{product.name} added to cart',
                'cart_count': cart_count,
                'cart_total': float(cart_total),
                'cart_tax': float(cart_tax),
                'cart_final_total': float(cart_final_total)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class UpdateCartView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cart_id = data.get('cart_id')
            quantity = int(data.get('quantity'))
            
            print(f"UpdateCartView: cart_id={cart_id}, quantity={quantity}")  # Debug log
            
            cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
            
            if quantity <= 0:
                print(f"Deleting cart item {cart_id} (quantity={quantity})")
                cart_item.delete()
            else:
                if cart_item.product.stock_quantity < quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Insufficient stock. Only {cart_item.product.stock_quantity} available.'
                    })
                print(f"Updating cart item {cart_id} quantity to {quantity}")
                cart_item.quantity = quantity
                cart_item.save()
            
            # Calculate new cart totals
            cart_items = Cart.objects.filter(user=request.user).select_related('product')
            cart_total = sum(item.quantity * item.product.selling_price for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)
            cart_tax = cart_total * Decimal('0.1')
            cart_final_total = cart_total + cart_tax
            
            print(f"Cart updated - total: {cart_total}, count: {cart_count}")  # Debug log
            
            return JsonResponse({
                'status': 'success',
                'cart_count': cart_count,
                'cart_total': float(cart_total),
                'cart_tax': float(cart_tax),
                'cart_final_total': float(cart_final_total)
            })
            
        except Exception as e:
            print(f"Error in UpdateCartView: {str(e)}")  # Debug log
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class RemoveFromCartView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cart_id = data.get('cart_id')
            
            cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
            product_name = cart_item.product.name
            cart_item.delete()
            
            # Calculate new cart totals
            cart_items = Cart.objects.filter(user=request.user).select_related('product')
            cart_total = sum(item.quantity * item.product.selling_price for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)
            cart_tax = cart_total * Decimal('0.1')
            cart_final_total = cart_total + cart_tax
            
            return JsonResponse({
                'status': 'success',
                'message': f'{product_name} removed from cart',
                'cart_count': cart_count,
                'cart_total': float(cart_total),
                'cart_tax': float(cart_tax),
                'cart_final_total': float(cart_final_total)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class ClearCartView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            Cart.objects.filter(user=request.user).delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Cart cleared',
                'cart_count': 0,
                'cart_total': 0,
                'cart_tax': 0,
                'cart_final_total': 0
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })


@method_decorator(csrf_exempt, name='dispatch')
class CheckoutView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method')
            amount_paid = Decimal(str(data.get('amount_paid', 0)))
            
            # Optimized cart query
            cart_items = Cart.objects.filter(user=request.user).select_related('product')
            
            if not cart_items.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cart is empty'
                })
            
            # Calculate totals
            subtotal = sum(item.quantity * item.product.selling_price for item in cart_items)
            tax_amount = subtotal * Decimal('0.1')
            total_amount = subtotal + tax_amount
            
            # Validate payment amount for cash transactions
            if payment_method.lower() == 'cash':
                if amount_paid <= 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please enter a valid cash amount',
                        'error_type': 'invalid_amount'
                    })
                
                if amount_paid < total_amount:
                    shortage = total_amount - amount_paid
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Insufficient cash payment. Short by ₱{shortage:.2f}',
                        'error_type': 'insufficient_cash',
                        'details': {
                            'total_required': float(total_amount),
                            'amount_given': float(amount_paid),
                            'shortage': float(shortage)
                        }
                    })
            
            # Validate payment amount for other methods
            elif payment_method.lower() in ['card', 'mobile', 'check']:
                if amount_paid != total_amount:
                    # For non-cash payments, amount should equal total
                    amount_paid = total_amount
            
            change_amount = amount_paid - total_amount if payment_method.lower() == 'cash' else Decimal('0')
            
            with transaction.atomic():
                # Create sale
                sale = Sale.objects.create(
                    cashier=request.user,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    payment_method=payment_method.upper(),  # Convert to uppercase to match model choices
                    amount_paid=amount_paid,
                    change_amount=change_amount,
                    status='COMPLETED'  # Use uppercase to match model choices
                )
                
                # Create sale items and update stock
                for cart_item in cart_items:
                    # Check stock availability again
                    if cart_item.product.stock_quantity < cart_item.quantity:
                        raise Exception(f'Insufficient stock for {cart_item.product.name}')
                    
                    # Create sale item
                    SaleItem.objects.create(
                        sale=sale,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.selling_price
                    )
                    
                    # Update stock
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()
                    
                    # Create stock movement record (stock already updated manually above)
                    StockMovement.objects.create(
                        product=cart_item.product,
                        movement_type='SALE',  # Use SALE for sales transactions
                        quantity=cart_item.quantity,
                        reason='sale',
                        reference=sale.sale_number,
                        user=request.user
                    )
                
                # Clear cart
                cart_items.delete()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Sale completed successfully',
                    'sale_id': sale.id,
                    'sale_number': sale.sale_number,
                    'total_amount': float(total_amount),
                    'change_amount': float(change_amount)
                })
                
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid payment amount or data format',
                'error_type': 'validation_error'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request format',
                'error_type': 'request_error'
            })
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Checkout error: {str(e)}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'Transaction failed: {str(e)}',
                'error_type': 'general_error'
            })


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'pos/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Sale.objects.select_related('cashier').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(sale_number__icontains=search) |
                Q(cashier__username__icontains=search) |
                Q(cashier__first_name__icontains=search) |
                Q(cashier__last_name__icontains=search)
            )
        
        # Date filter
        date_filter = self.request.GET.get('date')
        if date_filter:
            queryset = queryset.filter(created_at__date=date_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        from django.db.models import Sum
        
        # Calculate summary statistics
        all_sales = Sale.objects.filter(status='COMPLETED')
        context['total_revenue'] = all_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Today's statistics
        today = timezone.now().date()
        today_sales = all_sales.filter(created_at__date=today)
        context['today_sales_count'] = today_sales.count()
        context['today_revenue'] = today_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        return context


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'pos/sale_detail.html'
    context_object_name = 'sale'
    
    def get_object(self, queryset=None):
        """Ensure users can only access sales from their store or that they created"""
        obj = super().get_object(queryset)
        
        # Allow superusers to view all sales
        if self.request.user.is_superuser:
            return obj
            
        # For regular users, only allow access to sales they created
        # This prevents IDOR attacks
        if obj.cashier != self.request.user:
            from django.http import Http404
            raise Http404("Sale not found")
            
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale_items'] = self.object.items.select_related('product')
        return context


class ReceiptView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'pos/receipt.html'
    context_object_name = 'sale'
    
    def get_object(self, queryset=None):
        """Ensure users can only access receipts for sales they created"""
        obj = super().get_object(queryset)
        
        # Allow superusers to view all receipts
        if self.request.user.is_superuser:
            return obj
            
        # For regular users, only allow access to sales they created
        if obj.cashier != self.request.user:
            from django.http import Http404
            raise Http404("Receipt not found")
            
        return obj


class SalesReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'pos/sales_reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Today's sales
        today = date.today()
        today_sales = Sale.objects.filter(created_at__date=today, status='completed')
        context['today_sales_count'] = today_sales.count()
        context['today_sales_total'] = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # This month's sales
        this_month = today.replace(day=1)
        month_sales = Sale.objects.filter(created_at__date__gte=this_month, status='completed')
        context['month_sales_count'] = month_sales.count()
        context['month_sales_total'] = month_sales.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Recent sales
        context['recent_sales'] = Sale.objects.select_related('cashier').order_by('-created_at')[:10]
        
        return context


class ProductSearchAPIView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(sku__icontains=query) | Q(barcode__icontains=query),
            is_active=True,
            stock_quantity__gt=0
        ).select_related('category')[:10]
        
        data = [{
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'barcode': p.barcode,
            'price': str(p.selling_price),
            'stock': p.stock_quantity,
            'category': p.category.name if p.category else 'Uncategorized',
            'image': p.image.url if p.image else None
        } for p in products]
        
        return JsonResponse({'products': data})
