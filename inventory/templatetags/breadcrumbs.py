from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def breadcrumbs(context):
    """Generate breadcrumb navigation based on current URL"""
    request = context['request']
    
    try:
        url_name = request.resolver_match.url_name
        app_name = request.resolver_match.app_name
    except:
        # Fallback if no resolver match
        return mark_safe('')
    
    breadcrumb_map = {
        # Dashboard
        'dashboard': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': True}
        ],
        
        # Product URLs
        'product_list': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Products', 'url': 'inventory:product_list', 'active': True}
        ],
        'product_create': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Products', 'url': 'inventory:product_list', 'active': False},
            {'name': 'Add Product', 'url': '#', 'active': True}
        ],
        'product_detail': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Products', 'url': 'inventory:product_list', 'active': False},
            {'name': 'Product Details', 'url': '#', 'active': True}
        ],
        'product_edit': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Products', 'url': 'inventory:product_list', 'active': False},
            {'name': 'Edit Product', 'url': '#', 'active': True}
        ],
        'archived_products': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Archived Products', 'url': 'inventory:archived_products', 'active': True}
        ],
        
        # Category URLs
        'category_list': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Categories', 'url': 'inventory:category_list', 'active': True}
        ],
        'category_create': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Categories', 'url': 'inventory:category_list', 'active': False},
            {'name': 'Add Category', 'url': '#', 'active': True}
        ],
        'category_edit': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Categories', 'url': 'inventory:category_list', 'active': False},
            {'name': 'Edit Category', 'url': '#', 'active': True}
        ],
        'category_delete': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Categories', 'url': 'inventory:category_list', 'active': False},
            {'name': 'Delete Category', 'url': '#', 'active': True}
        ],
        
        # Profile URLs
        'profile_view': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Profile', 'url': 'inventory:profile_view', 'active': True}
        ],
        'profile_edit': [
            {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': False},
            {'name': 'Profile', 'url': 'inventory:profile_view', 'active': False},
            {'name': 'Edit Profile', 'url': '#', 'active': True}
        ],
    }
    
    # Get breadcrumbs for current URL
    breadcrumbs_list = breadcrumb_map.get(url_name, [
        {'name': 'Dashboard', 'url': 'inventory:dashboard', 'active': True}
    ])
    
    # Generate HTML
    html = '<nav class="flex mb-4" aria-label="Breadcrumb">'
    html += '<ol class="inline-flex items-center space-x-1 md:space-x-3">'
    
    for i, breadcrumb in enumerate(breadcrumbs_list):
        if i == 0:
            # First item (home icon)
            html += '<li class="inline-flex items-center">'
            if breadcrumb['active']:
                html += f'<span class="text-gray-500 text-sm font-medium">'
                html += '<i class="fas fa-home mr-2"></i>'
                html += f'{breadcrumb["name"]}</span>'
            else:
                try:
                    url = reverse(breadcrumb["url"])
                    html += f'<a href="{url}" class="text-gray-700 hover:text-blue-600 text-sm font-medium">'
                    html += '<i class="fas fa-home mr-2"></i>'
                    html += f'{breadcrumb["name"]}</a>'
                except:
                    html += f'<span class="text-gray-500 text-sm font-medium">'
                    html += '<i class="fas fa-home mr-2"></i>'
                    html += f'{breadcrumb["name"]}</span>'
            html += '</li>'
        else:
            # Other items
            html += '<li>'
            html += '<div class="flex items-center">'
            html += '<i class="fas fa-chevron-right text-gray-400 text-xs mx-2"></i>'
            if breadcrumb['active']:
                html += f'<span class="text-gray-500 text-sm font-medium">{breadcrumb["name"]}</span>'
            else:
                if breadcrumb['url'] != '#':
                    try:
                        url = reverse(breadcrumb["url"])
                        html += f'<a href="{url}" class="text-gray-700 hover:text-blue-600 text-sm font-medium">{breadcrumb["name"]}</a>'
                    except:
                        html += f'<span class="text-gray-500 text-sm font-medium">{breadcrumb["name"]}</span>'
                else:
                    html += f'<span class="text-gray-500 text-sm font-medium">{breadcrumb["name"]}</span>'
            html += '</div>'
            html += '</li>'
    
    html += '</ol>'
    html += '</nav>'
    
    return mark_safe(html)