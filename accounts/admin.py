from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, CompanySettings


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'employee_id', 'phone', 'hire_date', 'is_active']
    list_filter = ['role', 'is_active', 'hire_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'logo', 'address', 'phone', 'email', 'website')
        }),
        ('Business Settings', {
            'fields': ('tax_rate', 'currency_symbol', 'receipt_footer')
        }),
        ('Theme Settings', {
            'fields': ('primary_color', 'secondary_color')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not CompanySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
