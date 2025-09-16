from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from accounts.models import UserProfile
from .models import Product, Category, Supplier, StockMovement

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'bio', 'phone', 'date_of_birth', 
            'address', 'job_title', 'department', 'hire_date',
            'theme_preference'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your address'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sales Associate, Manager'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sales, Inventory, Management'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class UserAccountForm(forms.ModelForm):
    """Form for editing basic user account information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
        }

class ProductForm(forms.ModelForm):
    """Enhanced product form with better styling"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'supplier', 'sku', 'barcode',
            'cost_price', 'selling_price', 'stock_quantity', 'minimum_stock',
            'image', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter barcode (optional)'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'minimum_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class CategoryForm(forms.ModelForm):
    """Form for category management"""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            })
        }

class SupplierForm(forms.ModelForm):
    """Form for supplier management"""
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter supplier address'
            })
        }

class StockMovementForm(forms.ModelForm):
    """Form for stock movement management"""
    
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reason', 'reference']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter reason for stock movement'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter reference number (optional)'
            })
        }