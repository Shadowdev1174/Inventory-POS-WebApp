from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    TemplateView, UpdateView, ListView, CreateView, DeleteView
)
from django.urls import reverse_lazy
from .models import UserProfile, CompanySettings


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['phone', 'address', 'profile_picture']
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.can_access_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('inventory:dashboard')
        return super().dispatch(request, *args, **kwargs)


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.can_access_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('inventory:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password('defaultpassword123')  # Set default password
        user.save()
        messages.success(self.request, f'User {user.username} created successfully! Default password: defaultpassword123')
        return super().form_valid(form)


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.can_access_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('inventory:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.can_access_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('inventory:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CompanySettingsView(LoginRequiredMixin, UpdateView):
    model = CompanySettings
    fields = ['company_name', 'logo', 'address', 'phone', 'email', 'website', 'tax_rate', 'currency_symbol', 'receipt_footer', 'primary_color', 'secondary_color']
    template_name = 'accounts/company_settings.html'
    success_url = reverse_lazy('accounts:company_settings')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.can_access_admin():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('inventory:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        return CompanySettings.get_settings()
    
    def form_valid(self, form):
        messages.success(self.request, 'Company settings updated successfully!')
        return super().form_valid(form)
