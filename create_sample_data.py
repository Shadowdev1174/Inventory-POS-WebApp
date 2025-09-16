from inventory.models import Category, Product

# Create a simple category
cat, created = Category.objects.get_or_create(name='Food', defaults={'description': 'Food items'})
print(f'Category created: {created}')

# Create some simple products
products = [
    {'name': 'Burger', 'selling_price': 10.99, 'stock_quantity': 50},
    {'name': 'Pizza', 'selling_price': 15.99, 'stock_quantity': 30},
    {'name': 'Fries', 'selling_price': 4.99, 'stock_quantity': 100},
    {'name': 'Coke', 'selling_price': 2.99, 'stock_quantity': 200},
]

for p in products:
    product, created = Product.objects.get_or_create(
        name=p['name'],
        defaults={
            'selling_price': p['selling_price'],
            'cost_price': p['selling_price'],
            'stock_quantity': p['stock_quantity'],
            'minimum_stock': 5,
            'category': cat,
            'is_active': True
        }
    )
    print(f"{p['name']} created: {created}")

print('Sample data created successfully!')
