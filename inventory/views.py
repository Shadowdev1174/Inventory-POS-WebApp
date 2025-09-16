from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse, Http404
from .models import Product, Category, Supplier, StockMovement
from accounts.models import UserProfile
from .forms import UserProfileForm, UserAccountForm
import logging

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics - only active products
        context['total_products'] = Product.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.count()
        context['total_suppliers'] = 0  # Simplified - no suppliers
        context['archived_products'] = Product.all_objects.filter(is_deleted=True).count()
        
        # Low stock products - only active products
        context['low_stock_products'] = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=F('minimum_stock')
        )[:5]
        
        # Recent stock movements
        context['recent_movements'] = StockMovement.objects.select_related(
            'product', 'user'
        ).order_by('-created_at')[:10]
        
        # Stock value - only active products
        total_stock_value = Product.objects.filter(is_active=True).aggregate(
            total=Sum(F('stock_quantity') * F('cost_price'))
        )['total'] or 0
        context['total_stock_value'] = total_stock_value
        
        return context


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 24
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').order_by('name')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Stock filter
        stock_filter = self.request.GET.get('stock')
        if stock_filter == 'low':
            queryset = queryset.filter(stock_quantity__lte=F('minimum_stock'), stock_quantity__gt=0)
        elif stock_filter == 'out':
            queryset = queryset.filter(stock_quantity=0)
        elif stock_filter == 'good':
            queryset = queryset.filter(stock_quantity__gt=F('minimum_stock'))
        
        # Price range filter
        price_range = self.request.GET.get('price_range')
        if price_range == '0-10':
            queryset = queryset.filter(selling_price__lte=10)
        elif price_range == '10-50':
            queryset = queryset.filter(selling_price__gt=10, selling_price__lte=50)
        elif price_range == '50-100':
            queryset = queryset.filter(selling_price__gt=50, selling_price__lte=100)
        elif price_range == '100+':
            queryset = queryset.filter(selling_price__gt=100)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'name')
        valid_sorts = [
            'name', '-name', 'selling_price', '-selling_price', 
            'stock_quantity', '-stock_quantity', '-created_at', 'created_at'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_deleted=False))
        ).order_by('name')
        context['total_products'] = Product.objects.count()
        
        # Add filter states for template
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_stock'] = self.request.GET.get('stock', '')
        context['current_price_range'] = self.request.GET.get('price_range', '')
        context['current_sort'] = self.request.GET.get('sort', 'name')
        
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'
    
    def get_object(self, queryset=None):
        """Override to add security check and logging"""
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404("Product not found")
        
        # Use get_object_or_404 for security
        obj = get_object_or_404(Product, pk=pk)
        
        # Add logging for audit trail
        logger.info(f"User {self.request.user.username} viewed product {obj.id}")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_movements'] = self.object.stock_movements.select_related('user').order_by('-created_at')[:20]
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'image', 'selling_price', 'stock_quantity', 'category']
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        # Set default values for hidden fields
        form.instance.cost_price = form.instance.selling_price
        form.instance.minimum_stock = 5
        form.instance.is_active = True
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'image', 'selling_price', 'stock_quantity', 'category']
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def get_object(self, queryset=None):
        """Override to add security check and logging"""
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404("Product not found")
        
        # Use get_object_or_404 for security
        obj = get_object_or_404(Product, pk=pk)
        
        # Add logging for audit trail
        logger.info(f"User {self.request.user.username} accessed product {obj.id} for editing")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def form_valid(self, form):
        # Update cost_price to match selling_price if needed
        if not form.instance.cost_price:
            form.instance.cost_price = form.instance.selling_price
            
        # Log the update
        logger.info(f"User {self.request.user.username} updated product {form.instance.id}")
        
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')
    
    def get_object(self, queryset=None):
        """Override to add security check and logging"""
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404("Product not found")
        
        # Use get_object_or_404 for security - use all_objects to include deleted items
        obj = get_object_or_404(Product.all_objects, pk=pk)
        
        # Add logging for audit trail
        logger.info(f"User {self.request.user.username} accessed product {obj.id} for deletion")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_soft_deleted'] = self.object.is_deleted
        return context
    
    def delete(self, request, *args, **kwargs):
        """Handle both soft delete and hard delete"""
        self.object = self.get_object()
        
        # Check if it's a hard delete request
        if 'hard_delete' in request.POST:
            # Permanent deletion
            product_id = self.object.id
            product_name = self.object.name
            logger.warning(f"User {request.user.username} permanently deleted product {product_id}")
            self.object.hard_delete()
            messages.success(request, f'Product "{product_name}" permanently deleted!')
        else:
            # Soft delete (archive)
            if self.object.is_deleted:
                # Restore if already deleted
                self.object.restore()
                logger.info(f"User {request.user.username} restored product {self.object.id}")
                messages.success(request, f'Product "{self.object.name}" restored successfully!')
            else:
                # Soft delete
                self.object.soft_delete(user=request.user)
                logger.info(f"User {request.user.username} archived product {self.object.id}")
                messages.success(request, f'Product "{self.object.name}" archived successfully!')
        
        return redirect(self.success_url)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for delete operations"""
        return self.delete(request, *args, **kwargs)


# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def get_object(self, queryset=None):
        """Override to add security check and logging"""
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404("Category not found")
        
        # Use get_object_or_404 for security
        obj = get_object_or_404(Category, pk=pk)
        
        # Add logging for audit trail
        logger.info(f"User {self.request.user.username} accessed category {obj.id} for editing")
        
        return obj
    
    def form_valid(self, form):
        logger.info(f"User {self.request.user.username} updated category {form.instance.id}")
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')
    
    def get_object(self, queryset=None):
        """Override to add security check and logging"""
        pk = self.kwargs.get('pk')
        if not pk:
            raise Http404("Category not found")
        
        # Use get_object_or_404 for security
        obj = get_object_or_404(Category, pk=pk)
        
        # Add logging for audit trail
        logger.info(f"User {self.request.user.username} accessed category {obj.id} for deletion")
        
        return obj
    
    def delete(self, request, *args, **kwargs):
        category_id = self.get_object().id
        logger.warning(f"User {request.user.username} deleted category {category_id}")
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ArchivedProductsView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/archived_products.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        """Return only soft-deleted products"""
        queryset = Product.all_objects.filter(is_deleted=True).select_related('category', 'supplier').order_by('-deleted_at')
        
        # Search functionality for archived products
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_archived'] = Product.all_objects.filter(is_deleted=True).count()
        return context


# New enhanced views for bulk operations and export

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime


@login_required
@require_POST
@csrf_protect
def bulk_archive_products(request):
    """Bulk archive selected products"""
    product_ids = request.POST.get('product_ids', '').split(',')
    product_ids = [pid.strip() for pid in product_ids if pid.strip()]
    
    if not product_ids:
        messages.error(request, 'No products selected for archiving.')
        return redirect('inventory:product_list')
    
    try:
        # Get products and perform soft delete
        products = Product.objects.filter(id__in=product_ids, is_deleted=False)
        archived_count = 0
        
        for product in products:
            product.soft_delete(user=request.user)
            archived_count += 1
            logger.info(f"User {request.user.username} bulk archived product {product.id} ({product.name})")
        
        messages.success(request, f'Successfully archived {archived_count} product(s).')
        
    except Exception as e:
        logger.error(f"Error in bulk archive: {e}")
        messages.error(request, 'An error occurred while archiving products.')
    
    return redirect('inventory:product_list')


@login_required
@require_POST
@csrf_protect
def bulk_delete_products(request):
    """Bulk hard delete selected products"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to permanently delete products.')
        return redirect('inventory:product_list')
    
    product_ids = request.POST.get('product_ids', '').split(',')
    product_ids = [pid.strip() for pid in product_ids if pid.strip()]
    
    if not product_ids:
        messages.error(request, 'No products selected for deletion.')
        return redirect('inventory:product_list')
    
    try:
        # Get products and perform hard delete
        products = Product.all_objects.filter(id__in=product_ids)
        deleted_count = products.count()
        
        for product in products:
            logger.warning(f"User {request.user.username} permanently deleted product {product.id} ({product.name})")
        
        products.delete()
        messages.success(request, f'Successfully deleted {deleted_count} product(s) permanently.')
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        messages.error(request, 'An error occurred while deleting products.')
    
    return redirect('inventory:product_list')


@login_required
def export_products(request):
    """Export products to CSV or PDF"""
    if request.method != 'POST':
        return redirect('inventory:product_list')
    
    export_format = request.POST.get('format', 'csv')
    selected_products = request.POST.get('selected_products', '')
    include_images = request.POST.get('include_images') == '1'
    include_stock_value = request.POST.get('include_stock_value') == '1'
    
    # Get products to export
    if selected_products:
        product_ids = [pid.strip() for pid in selected_products.split(',') if pid.strip()]
        products = Product.objects.filter(id__in=product_ids).select_related('category').order_by('name')
    else:
        products = Product.objects.select_related('category').order_by('name')
    
    if export_format == 'csv':
        return export_products_csv(products, include_stock_value)
    elif export_format == 'pdf':
        return export_products_pdf(products, include_images, include_stock_value)
    else:
        messages.error(request, 'Invalid export format.')
        return redirect('inventory:product_list')


def export_products_csv(products, include_stock_value=True):
    """Export products to CSV format"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # CSV Headers
    headers = ['Name', 'SKU', 'Barcode', 'Category', 'Selling Price', 'Cost Price', 'Stock Quantity', 'Minimum Stock', 'Status']
    if include_stock_value:
        headers.extend(['Stock Value', 'Potential Revenue'])
    headers.extend(['Created Date', 'Last Updated'])
    
    writer.writerow(headers)
    
    # CSV Data
    for product in products:
        row = [
            product.name,
            product.sku,
            product.barcode or '',
            product.category.name if product.category else 'No Category',
            f"₱{product.selling_price:.2f}",
            f"₱{product.cost_price:.2f}",
            product.stock_quantity,
            product.minimum_stock,
            'Active' if product.is_active else 'Inactive'
        ]
        
        if include_stock_value:
            stock_value = product.stock_quantity * product.cost_price
            potential_revenue = product.stock_quantity * product.selling_price
            row.extend([f"₱{stock_value:.2f}", f"₱{potential_revenue:.2f}"])
        
        row.extend([
            product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
        writer.writerow(row)
    
    return response


def export_products_pdf(products, include_images=False, include_stock_value=True):
    """Export products to PDF format"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Title
    title = Paragraph(f"Products Inventory Report", title_style)
    elements.append(title)
    
    # Export info
    export_info = Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>"
        f"Total Products: {products.count()}<br/>"
        f"Exported by: {getattr(products.first(), 'user', 'System') if products.exists() else 'System'}",
        styles['Normal']
    )
    elements.append(export_info)
    elements.append(Spacer(1, 20))
    
    # Table data
    if include_stock_value:
        table_data = [['Name', 'Category', 'SKU', 'Price', 'Stock', 'Stock Value']]
    else:
        table_data = [['Name', 'Category', 'SKU', 'Price', 'Stock', 'Status']]
    
    for product in products:
        if include_stock_value:
            stock_value = product.stock_quantity * product.cost_price
            row = [
                product.name[:30],  # Truncate long names
                product.category.name if product.category else 'No Category',
                product.sku,
                f"₱{product.selling_price:.2f}",
                str(product.stock_quantity),
                f"₱{stock_value:.2f}"
            ]
        else:
            row = [
                product.name[:30],
                product.category.name if product.category else 'No Category',
                product.sku,
                f"₱{product.selling_price:.2f}",
                str(product.stock_quantity),
                'Active' if product.is_active else 'Inactive'
            ]
        table_data.append(row)
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="products_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response


@login_required
def product_quick_edit(request, pk):
    """Quick edit product via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        product = get_object_or_404(Product, pk=pk)
        
        # Update fields
        if 'selling_price' in request.POST:
            product.selling_price = float(request.POST['selling_price'])
        if 'stock_quantity' in request.POST:
            product.stock_quantity = int(request.POST['stock_quantity'])
        if 'minimum_stock' in request.POST:
            product.minimum_stock = int(request.POST['minimum_stock'])
        
        product.save()
        
        logger.info(f"User {request.user.username} quick-edited product {product.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Product updated successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'selling_price': float(product.selling_price),
                'stock_quantity': product.stock_quantity,
                'minimum_stock': product.minimum_stock
            }
        })
        
    except Exception as e:
        logger.error(f"Error in quick edit: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


# Profile Views
class ProfileView(LoginRequiredMixin, TemplateView):
    """View for displaying user profile"""
    template_name = 'inventory/profile/profile_view.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        context['user'] = self.request.user
        
        # Get some user statistics
        context['total_products_created'] = Product.objects.filter(
            stock_movements__user=self.request.user,
            stock_movements__movement_type='IN'
        ).distinct().count()
        
        context['recent_activities'] = StockMovement.objects.filter(
            user=self.request.user
        ).select_related('product').order_by('-created_at')[:5]
        
        return context


@login_required
def profile_edit(request):
    """View for editing user profile"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserAccountForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('inventory:profile_view')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserAccountForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    }
    
    return render(request, 'inventory/profile/profile_edit.html', context)


@login_required
def update_theme_preference(request):
    """AJAX view to update user's theme preference"""
    if request.method == 'POST':
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.theme_preference = theme
            profile.save()
            return JsonResponse({'success': True, 'theme': theme})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
